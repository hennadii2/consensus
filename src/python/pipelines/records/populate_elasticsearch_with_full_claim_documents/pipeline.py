import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from claim_pb2 import ClaimNamespace
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.beam.records.full_merged_feature_record import (
    FullMergedFeatureRecord,
    read_qualifying_merged_feature_records_from_parquet,
)
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.models.study_type_classifier import study_type_or_none_if_below_threshold
from common.search.claim_index import ClaimIndex, claim_to_document
from common.search.claim_util import generate_base_claim
from common.search.connect import ElasticClient, SearchEnv
from common.search.search_util import quantize_vector
from elasticsearch.helpers import streaming_bulk
from paper_metadata_pb2 import PaperMetadata


@dataclass(frozen=True)
class PopulateFullClaimDocumentsResult(PipelineResult):
    paper_id: str
    claim_id: str
    search_index_id: str
    dry_run: bool


# TODO(meganvw): Move to common lib for easy re-use
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


class PopulateFullClaimDocuments(beam.DoFn):
    """
    DoFn to write claims that meet a threshold to a new index in elasticsearch.
    """

    # Number of records to write to search index in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        search_env: SearchEnv,
        project_id: str,
        search_index_id: str,
        quantize_vectors: bool,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.search_env = search_env
        self.project_id = project_id
        self.search_index_id = search_index_id
        self.quantize_vectors = quantize_vectors

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.db = MainDbClient(self.db_env)
        self.journals = Journals(self.db)
        self.journal_scores = JournalScores(self.db)

        if not self.dry_run:
            self.es_connection = ElasticClient(self.search_env)
            self.claim_index = ClaimIndex(self.es_connection, self.search_index_id)
            self.commit_buffer = []

    def flush_commit_buffer(self):
        if not self.dry_run:
            try:
                failures = 0
                for ok, action in streaming_bulk(
                    client=self.claim_index.es,
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
                    "populate_full_claim_document/process", "flush_commit_buffer_failures"
                ).inc(failures)
                beam.metrics.Metrics.counter(
                    "populate_full_claim_document/process", "flush_commit_buffer_successes"
                ).inc(len(self.commit_buffer) - failures)
            except Exception as e:
                logging.error(f"Failed commit: {e}")
                beam.metrics.Metrics.counter(
                    "populate_full_claim_document/process", "commit_failure"
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
                "populate_full_claim_document/process", "added_study_type"
            ).inc()
        if "fields_of_study" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_paper_document/process", "added_fields_of_study"
            ).inc()
        if "sjr_best_quartile" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_sjr_best_quartile"
            ).inc()
        if "is_biomed_plus" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_is_biomed_plus"
            ).inc()
        if "controlled_study_type" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_controlled_study_type"
            ).inc()
        if "population_type" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_population_type"
            ).inc()
        if "is_rct_review" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_is_rct_review"
            ).inc()
        if "sample_size" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_sample_size"
            ).inc()
        if "study_count" in document_dict:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "added_study_count"
            ).inc()

    def process(
        self, record: Optional[FullMergedFeatureRecord]
    ) -> Iterator[PopulateFullClaimDocumentsResult]:
        if record is None or record.metadata is None:
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "unexpected_skip_none_record"
            ).inc()
            return

        try:
            claim = generate_base_claim(
                namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                display_text=(
                    record.enhanced_claim if record.enhanced_claim else record.modified_claim
                ),
                original_text=record.sentence,
                probability=record.claim_probability,
                paper_id=record.paper_id,
                paper_metadata=record.metadata,
                is_enhanced=bool(record.enhanced_claim),
            )
            # TODO(meganvw): Move embedding setting into an updated
            # generate_claim function that does not re-generate the embeddings.
            claim.metadata.embedding[:] = record.claim_embeddings
            claim.metadata.title_embedding[:] = record.title_embeddings

            search_index_document = claim_to_document(
                claim,
                with_split_title_embedding=True,
                allow_empty_embeddings=False,
            )
            document_dict = search_index_document.dict()
            if self.quantize_vectors:
                document_dict["embedding"] = quantize_vector(document_dict["embedding"])
                document_dict["title_embedding"] = quantize_vector(
                    document_dict["title_embedding"]
                )

            # TODO(meganvw): Move setting of feature fields into strongly typed
            # objects so that we are not free typing the field names here
            document_dict["fields_of_study"] = (
                None
                if record.metadata.fields_of_study is None
                else list(set(x.string_data for x in record.metadata.fields_of_study))
            )
            document_dict["study_type"] = study_type_or_none_if_below_threshold(
                study_type=record.study_type_prediction.value,
                probability=record.study_type_max_probability,
            )
            document_dict["sjr_best_quartile"] = get_scimago_quartile(
                journals=self.journals,
                journal_scores=self.journal_scores,
                paper_metadata=record.metadata,
            )
            document_dict["is_biomed_plus"] = record.BiomedPlus
            document_dict["controlled_study_type"] = (
                None
                if record.controlled_study_prediction is None
                else record.controlled_study_prediction.value
            )
            document_dict["population_type"] = (
                None
                if record.human_classifier_prediction is None
                else record.human_classifier_prediction.value
            )
            document_dict["is_rct_review"] = record.review_rct_classifier_prediction
            document_dict["sample_size"] = record.sample_size_prediction
            document_dict["study_count"] = record.study_count_prediction

            # Drop all None types from the dict
            document_dict = {k: v for k, v in document_dict.items() if v is not None}
            self._log_feature_counters(document_dict)
            beam.metrics.Metrics.counter(
                "populate_full_claim_document/process", "generated_claim"
            ).inc()

            if not self.dry_run:
                self.commit_buffer.append(
                    {
                        "_index": self.claim_index.name,
                        "_source": document_dict,
                    }
                )
                beam.metrics.Metrics.counter(
                    "populate_full_claim_document/process", "append_claim_to_buffer"
                ).inc()
                if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                    self.flush_commit_buffer()

            yield PopulateFullClaimDocumentsResult(
                paper_id=record.paper_id,
                claim_id=record.claim_id,
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            beam.metrics.Metrics.counter("populate_full_claim_document/process", "error").inc()
            logging.error(e)
            yield PopulateFullClaimDocumentsResult(
                paper_id=record.paper_id,
                claim_id=record.claim_id,
                search_index_id=self.search_index_id,
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
    db_env: DbEnv,
    search_env: SearchEnv,
    input_patterns: list[str],
    quantize_vectors: bool,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    search_index_id = config.job_name
    search = ElasticClient(search_env)
    claim_index = ClaimIndex(search, search_index_id)
    if claim_index.exists():
        print("ERROR: Claim index already exists")
        return

    if not dry_run:
        claim_index.create()

    with beam.Pipeline(options=pipeline_options) as p:
        results = read_qualifying_merged_feature_records_from_parquet(
            p, input_patterns=input_patterns
        ) | "PopulateFullClaimDocuments" >> beam.ParDo(
            PopulateFullClaimDocuments(
                dry_run=dry_run,
                db_env=db_env,
                search_env=search_env,
                project_id=project_id,
                search_index_id=search_index_id,
                quantize_vectors=quantize_vectors,
            )
        )

        write_pipeline_results(config.results_file, results)
