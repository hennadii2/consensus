import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.beam.records.full_merged_paper_feature_record import (
    FullMergedPaperFeatureRecord,
    read_qualifying_merged_paper_feature_records_from_parquet,
)
from common.config.secret_manager import SecretId
from common.db.connect import DbEnvInfo, MainDbClient
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.models.study_type_classifier import study_type_or_none_if_below_threshold
from common.search.connect import ElasticClient, SearchEnv
from common.search.paper_index import PaperIndex, PaperIndexDocument
from common.search.paper_util import PaperIdProvider, generate_hash_paper_id, generate_url_slug
from elasticsearch.helpers import streaming_bulk
from paper_metadata_pb2 import PaperMetadata, PaperProvider

# This ingest pipeline must be defined on the Elasticsearch cluster before running this pipeline
ELSER_ENRICH_PIPELINE = "add-elser-tokens-pipeline"


@dataclass(frozen=True)
class PopulateFullPaperDocumentsResult(PipelineResult):
    paper_id: str
    search_index_id: str
    dry_run: bool


# TODO(cvarano): optimize the `journal_util.py` query and use that
def get_scimago_quartile(
    journals: Journals,
    journal_scores: JournalScores,
    paper_metadata: PaperMetadata,
) -> Optional[int]:
    """
    Returns a scimago journal score for the paper if possible.
    """
    if not paper_metadata.journal_name and not paper_metadata.journal_id:
        return None

    journal_id = paper_metadata.journal_id
    if not journal_id:
        # Lookup the journal by name if an ID was not stored on the paper
        journal = journals.read_by_name(paper_metadata.journal_name)
        if journal:
            journal_id = journal.id

    if journal_id:
        # Lookup the journal score if a journal was found for the paper
        return journal_scores.get_latest_scimago_quartile(journal_id=journal_id)
    else:
        return None


class PopulateFullPaperDocuments(beam.DoFn):
    """
    DoFn to index papers in Elasticsearch.
    """

    # Number of records to write to search index in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env_info: DbEnvInfo,
        search_env: SearchEnv,
        project_id: str,
        search_index_name: str,
    ):
        self.dry_run = dry_run
        self.db_env_info = db_env_info
        self.search_env = search_env
        self.project_id = project_id
        self.search_index_name = search_index_name

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.db = MainDbClient(
            self.db_env_info.db_env,
            self.db_env_info.db_host_override,
            self.db_env_info.db_port_override,
        )
        self.journals = Journals(self.db)
        self.journal_scores = JournalScores(self.db)

        if not self.dry_run:
            self.es_connection = ElasticClient(self.search_env)
            self.paper_index = PaperIndex(self.es_connection, self.search_index_name)
            self.commit_buffer = []

    def flush_commit_buffer(self):
        if not self.dry_run:
            try:
                failures = 0
                for ok, action in streaming_bulk(
                    client=self.paper_index.es,
                    actions=self.commit_buffer,
                    chunk_size=150,
                    max_retries=3,
                    initial_backoff=1,
                    yield_ok=False,
                    raise_on_error=False,
                    raise_on_exception=False,
                ):
                    if not ok:
                        failures = failures + 1
                        logging.error(action)

                logging.info(f"Flush commit buffer failures: {failures}/{len(self.commit_buffer)}")
                beam.metrics.Metrics.counter(
                    "populate_full_paper_document/process", "flush_commit_buffer_failures"
                ).inc(failures)
                beam.metrics.Metrics.counter(
                    "populate_full_paper_document/process", "flush_commit_buffer_successes"
                ).inc(len(self.commit_buffer) - failures)
            except Exception as e:
                logging.error(f"Failed commit: {e}")
                beam.metrics.Metrics.counter(
                    "populate_full_paper_document/process", "commit_failure"
                ).inc(len(self.commit_buffer))

            del self.commit_buffer
            self.commit_buffer = []

    def finish_bundle(self):
        if not self.dry_run:
            self.flush_commit_buffer()

    def teardown(self):
        self.db.close()
        if not self.dry_run:
            self.es_connection.close()

    def _log_feature_counters(self, document_dict: dict[str, Any]) -> None:
        if "study_type" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_study_type"
            ).inc()
        if "fields_of_study" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_fields_of_study"
            ).inc()
        if "sjr_best_quartile" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_sjr_best_quartile"
            ).inc()
        if "is_biomed_plus" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_is_biomed_plus"
            ).inc()
        if "controlled_study_type" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_controlled_study_type"
            ).inc()
        if "population_type" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_population_type"
            ).inc()
        if "is_rct_review" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_is_rct_review"
            ).inc()
        if "sample_size" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_sample_size"
            ).inc()
        if "study_count" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_study_count"
            ).inc()

    def process(
        self, record: Optional[FullMergedPaperFeatureRecord]
    ) -> Iterator[PopulateFullPaperDocumentsResult]:
        if record is None or record.metadata is None:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "unexpected_skip_none_record"
            ).inc()
            return

        try:
            if record.metadata.provider == PaperProvider.SEMANTIC_SCHOLAR:
                provider = PaperIdProvider.S2
            else:
                beam.metrics.Metrics.counter(
                    "populate_full_paper_document/process", "unexpected_provider"
                ).inc()
                return

            paper = PaperIndexDocument(
                hash_paper_id=generate_hash_paper_id(provider, record.paper_id),
                paper_id=record.paper_id,
                abstract=record.abstract,
                title=record.metadata.title,
                publish_year=record.metadata.publish_year,
                citation_count=record.metadata.citation_count,
                url_slug=generate_url_slug(record.metadata),
                sjr_best_quartile=get_scimago_quartile(
                    journals=self.journals,
                    journal_scores=self.journal_scores,
                    paper_metadata=record.metadata,
                ),
                study_type=study_type_or_none_if_below_threshold(
                    study_type=(
                        None
                        if record.study_type_prediction is None
                        else record.study_type_prediction.value
                    ),
                    probability=record.study_type_max_probability,
                ),
                fields_of_study=(
                    None
                    if record.metadata.fields_of_study is None
                    else list(set(x.string_data for x in record.metadata.fields_of_study))
                ),
                is_biomed_plus=record.BiomedPlus,
                controlled_study_type=(
                    None
                    if record.controlled_study_prediction is None
                    else record.controlled_study_prediction.value
                ),
                population_type=(
                    None
                    if record.human_classifier_prediction is None
                    else record.human_classifier_prediction.value
                ),
                is_rct_review=record.review_rct_classifier_prediction,
                sample_size=record.sample_size_prediction,
                study_count=record.study_count_prediction,
            )

            # Drop all None types from the dict
            document_dict = {k: v for k, v in paper.dict().items() if v is not None}
            self._log_feature_counters(document_dict)
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "generated_paper"
            ).inc()

            if not self.dry_run:
                self.commit_buffer.append(
                    {
                        "_index": self.paper_index.name,
                        "pipeline": ELSER_ENRICH_PIPELINE,
                        "_source": document_dict,
                    }
                )
                beam.metrics.Metrics.counter(
                    "populate_full_paper_document/process", "append_paper_to_buffer"
                ).inc()
                if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                    self.flush_commit_buffer()

            yield PopulateFullPaperDocumentsResult(
                paper_id=record.paper_id,
                search_index_id=self.search_index_name,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            beam.metrics.Metrics.counter("populate_full_paper_document/process", "error").inc()
            logging.error(e)
            yield PopulateFullPaperDocumentsResult(
                paper_id=record.paper_id,
                search_index_id=self.search_index_name,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env_info: DbEnvInfo,
    search_env: SearchEnv,
    input_patterns: list[str],
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    search_index_name = config.job_name
    search = ElasticClient(search_env)
    paper_index = PaperIndex(search, search_index_name)
    if paper_index.exists():
        print("ERROR: Paper index already exists")
        return

    if not dry_run:
        paper_index.create()

    with beam.Pipeline(options=pipeline_options) as p:
        results = read_qualifying_merged_paper_feature_records_from_parquet(
            p, input_patterns=input_patterns
        ) | "PopulateFullPaperDocuments" >> beam.ParDo(
            PopulateFullPaperDocuments(
                dry_run=dry_run,
                db_env_info=db_env_info,
                search_env=search_env,
                project_id=project_id,
                search_index_name=search_index_name,
            )
        )

        write_pipeline_results(config.results_file, results)
