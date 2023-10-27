import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional, Tuple

import apache_beam as beam  # type: ignore
from apache_beam import metrics
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from claim_pb2 import ClaimNamespace
from common.beam.model_outputs import ModelOutput, read_qualifying_model_outputs_from_parquet
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.db.papers import Papers
from common.search.async_claim_index import AsyncClaimIndex
from common.search.claim_util import generate_stable_claim_id
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import scan, streaming_bulk
from journal_pb2 import JournalScoreProvider


class GenerateStableClaimIds(beam.DoFn):
    """
    DoFn to generate stable claim ids from ModelOutput objects.
    """

    def __init__(
        self,
        dry_run: bool,
        project_id: str,
        db_env: DbEnv,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.project_id = project_id

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to avoid having to pass it in as a parameter
        os.environ["GCLOUD_PROJECT_ID"] = self.project_id

        self.db = MainDbClient(self.db_env)
        self.papers = Papers(self.db)

    def teardown(self):
        self.db.close()
        self.papers.connection.close()

    def process(self, model_output: ModelOutput) -> Iterator[Tuple[str, Any]]:
        metrics.Metrics.counter(
            "search_index_update/generate_stable_claim_ids", "input_records"
        ).inc()
        paper_id = model_output.paper_id

        try:
            paper = self.papers.read_by_id(paper_id)
            if not paper:
                metrics.Metrics.counter(
                    "search_index_update/generate_stable_claim_ids", "paper_not_found_error"
                ).inc()
                raise ValueError(f"Failed to find paper for id {paper_id}")

            claim_id = generate_stable_claim_id(
                namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                original_claim_text=model_output.sentence,
                paper_title=paper.metadata.title,
            )

            metrics.Metrics.counter(
                "search_index_update/generate_stable_claim_ids", "output_records"
            ).inc()
            yield (claim_id, paper.metadata.journal_name)

        except Exception as e:
            metrics.Metrics.counter(
                "search_index_update/generate_stable_claim_ids", "total_errors"
            ).inc()
            logging.exception(f"Failed to generate stable claim id for paper {paper_id}: {e}")


class GetEmbeddingsById(beam.DoFn):
    """
    DoFn to retrieve embeddings from an Elasticsearch index by id.
    """

    # Number of records to write to search index in one commit
    MAX_SCROLL_SIZE = 10000

    def __init__(
        self,
        dry_run: bool,
        search_env: SearchEnv,
        db_env: DbEnv,
        project_id: str,
        search_index_id: str,
    ):
        self.dry_run = dry_run
        self.search_env = search_env
        self.db_env = db_env
        self.project_id = project_id
        self.search_index_id = search_index_id
        # Window is required for finish_bundle to emit values
        self.window = beam.transforms.window.GlobalWindow()

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        search = ElasticClient(self.search_env)
        self.claim_index = AsyncClaimIndex(search, self.search_index_id)

        self.script_fields = {
            "embedding": {
                "script": {
                    "source": "doc['embedding'].size() > 0 ? doc['embedding'].vectorValue : null"
                }
            },
            "title_embedding": {
                "script": {
                    "source": "doc['title_embedding'].size() > 0 ? doc['title_embedding'].vectorValue : null"  # noqa: E501
                }
            },
        }

        self.claim_ids = []
        self.claim_journal_dict = {}

    def teardown(self):
        self.claim_index.es.close()

    def finish_bundle(self):
        for result in self.scan_claim_ids():
            yield beam.utils.windowed_value.WindowedValue(
                value=result,
                timestamp=0,
                windows=[self.window],
            )

    def scan_claim_ids(self):
        metrics.Metrics.counter("search_index_update/get_embeddings", "scan_claim_ids_calls").inc()
        if not self.dry_run:
            query = {"query": {"ids": {"values": self.claim_ids}}}
            for hit in scan(
                client=self.claim_index.es,
                index=self.claim_index.name,
                query=query,
                scroll="5m",
                raise_on_error=False,
                script_fields=self.script_fields,
                size=max(len(self.claim_ids), self.MAX_SCROLL_SIZE),
            ):
                claim_id = hit["_id"]
                embedding_dict = {
                    "embedding": hit["fields"]["embedding"][0],
                    "title_embedding": hit["fields"]["title_embedding"][0],
                }
                output = (
                    claim_id,
                    self.claim_journal_dict[claim_id],
                    None if None in embedding_dict.values() else embedding_dict,
                )
                metrics.Metrics.counter(
                    "search_index_update/get_embeddings", "output_records"
                ).inc()
                yield output

            del self.claim_ids
            self.claim_ids = []

    def process(
        self, data: Tuple[str, Any], window=beam.DoFn.WindowParam
    ) -> Iterator[Tuple[str, Any, Any]]:
        metrics.Metrics.counter("search_index_update/get_embeddings", "input_records").inc()
        self.window = window
        claim_id, journal_name = data

        self.claim_journal_dict[claim_id] = journal_name
        self.claim_ids.append(claim_id)
        if len(self.claim_ids) == self.MAX_SCROLL_SIZE:
            for result in self.scan_claim_ids():
                yield result


@dataclass(frozen=True)
class UpdateSearchIndexResult(PipelineResult):
    claim_id: str
    journal_id: Optional[str]
    sjr_best_quartile: Optional[int]
    search_index_id: str
    dry_run: bool


class UpdateSearchIndex(beam.DoFn):
    """
    DoFn to delete existing claims from an existing elasticsearch index.
    """

    # Number of records to write to search index in one commit
    MAX_COMMIT_BATCH_COUNT = 150

    def __init__(
        self,
        dry_run: bool,
        search_env: SearchEnv,
        db_env: DbEnv,
        project_id: str,
        search_index_id: str,
    ):
        self.dry_run = dry_run
        self.search_env = search_env
        self.db_env = db_env
        self.project_id = project_id
        self.search_index_id = search_index_id

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        search = ElasticClient(self.search_env)
        self.claim_index = AsyncClaimIndex(search, self.search_index_id)

        self.db = MainDbClient(self.db_env)
        self.papers = Papers(self.db)
        self.journals = Journals(self.db)
        self.journal_scores = JournalScores(self.db)

        self.commit_buffer = []

    def flush_commit_buffer(self):
        failures = 0
        if not self.dry_run:
            for ok, action in streaming_bulk(
                client=self.claim_index.es,
                actions=self.commit_buffer,
                max_retries=3,
                yield_ok=False,
                raise_on_error=False,
                raise_on_exception=False,
            ):
                metrics.Metrics.counter(
                    "search_index_update/update", "sent_for_update_count"
                ).inc()
                if not ok:
                    metrics.Metrics.counter(
                        "search_index_update/update", "sent_for_update_not_ok_count"
                    ).inc()
                    failures = failures + 1
                    logging.error(action)
                    if failures == 1:
                        logging.info(f"commit example: {self.commit_buffer[0]}")

        logging.info(f"Flush commit buffer failures: {failures}/{len(self.commit_buffer)}")
        del self.commit_buffer
        self.commit_buffer = []

    def finish_bundle(self):
        self.flush_commit_buffer()

    def teardown(self):
        self.claim_index.es.close()
        self.db.close()
        self.papers.connection.close()
        self.journals.connection.close()
        self.journal_scores.connection.close()

    def process(self, data: Tuple[str, Any, Any]) -> Iterator[UpdateSearchIndexResult]:
        metrics.Metrics.counter("search_index_update/update", "input_records").inc()

        claim_id = data[0]
        journal_name = data[1]
        embedding_dict = data[2]

        try:
            journal = self.journals.read_by_name(journal_name)
            if not journal:
                metrics.Metrics.counter(
                    "search_index_update/update", "journal_not_found_error"
                ).inc()
                raise ValueError(f"Failed to find journal: {journal_name}")
            # TODO(cvarano): parameterize year
            year = 2021
            journal_score = self.journal_scores.get_score(
                journal.id, year, JournalScoreProvider.SCIMAGO
            )
            if not journal_score:
                metrics.Metrics.counter(
                    "search_index_update/update", "journal_score_not_found_error"
                ).inc()
                raise ValueError(f"Failed to find journal score for journal: {journal.id}")
            best_quartile = journal_score.metadata.scimago.best_quartile

            # Include `embedding` and `title_embedding` since they are excluded from _source, and
            # so would otherwise be dropped from any update requests.
            # https://www.elastic.co/guide/en/elasticsearch/reference/current/mapping-source-field.html#disable-source-field  # noqa: E501
            self.commit_buffer.append(
                {
                    "_op_type": "update",
                    "_index": self.claim_index.name,
                    "_id": claim_id,
                    "doc": {
                        "sjr_best_quartile": best_quartile,
                        "embedding": embedding_dict["embedding"],
                        "title_embedding": embedding_dict["title_embedding"],
                    },
                }
            )

            if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                self.flush_commit_buffer()

            metrics.Metrics.counter("search_index_update/update", "output_records").inc()
            yield UpdateSearchIndexResult(
                claim_id=claim_id,
                journal_id=journal.id,
                sjr_best_quartile=best_quartile,
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            metrics.Metrics.counter("search_index_update/update", "total_errors").inc()
            logging.error(e)
            yield UpdateSearchIndexResult(
                claim_id=claim_id,
                journal_id=None,
                sjr_best_quartile=None,
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_search_index_update_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    search_env: SearchEnv,
    input_file_pattern: str,
    search_index_id: str,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    with beam.Pipeline(options=pipeline_options) as p:
        columns = [
            "paper_id",
            "sentence",
            "modified_claim",
            "claim_probability",
        ]
        model_outputs = read_qualifying_model_outputs_from_parquet(
            p, input_file_pattern, columns=columns
        )

        results = (
            model_outputs
            | "GenerateStableClaimIds"
            >> beam.ParDo(
                GenerateStableClaimIds(dry_run=dry_run, db_env=db_env, project_id=project_id)
            )
            | "GetEmbeddingsByIdTest"
            >> beam.ParDo(
                GetEmbeddingsById(
                    dry_run=dry_run,
                    search_env=search_env,
                    db_env=db_env,
                    project_id=project_id,
                    search_index_id=search_index_id,
                )
            )
            | "FilterNoEmbedding" >> beam.Filter(lambda x: x[-1] is not None)
            | "UpdateSearchIndex"
            >> beam.ParDo(
                UpdateSearchIndex(
                    dry_run=dry_run,
                    search_env=search_env,
                    db_env=db_env,
                    project_id=project_id,
                    search_index_id=search_index_id,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
