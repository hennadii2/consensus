import logging
import os
from typing import Any, Iterator

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.records.embedding_record import ClaimEmbedding
from common.config.secret_manager import SecretId
from common.search.claim_index import ClaimIndex
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import streaming_bulk


class AddEmbeddingsToClaims(beam.DoFn):
    """
    DoFn to write claims that meet a threshold to a new index in elasticsearch.
    """

    # Number of records to write to search index in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        search_env: SearchEnv,
        project_id: str,
        search_index_id: str,
    ):
        self.dry_run = dry_run
        self.search_env = search_env
        self.project_id = project_id
        self.search_index_id = search_index_id

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

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
                    "process_paper_records/process", "flush_commit_buffer_failures"
                ).inc(failures)
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "flush_commit_buffer_successes"
                ).inc(len(self.commit_buffer) - failures)
            except Exception as e:
                logging.error(f"Failed commit: {e}")
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "commit_failure"
                ).inc(len(self.commit_buffer))

            del self.commit_buffer
            self.commit_buffer = []

    def finish_bundle(self):
        if not self.dry_run:
            self.flush_commit_buffer()

    def teardown(self):
        if not self.dry_run:
            self.es_connection.close()

    def process(self, record: ClaimEmbedding) -> Iterator[None]:
        try:
            beam.metrics.Metrics.counter(
                "process_paper_records/process", "process_embedding"
            ).inc()
            if not self.dry_run:
                self.commit_buffer.append(
                    {
                        "_index": self.claim_index.name,
                        "_id": record.claim_id,
                        "_op_type": "update",
                        "doc": {
                            "embedding": record.embeddings,
                        },
                    }
                )
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "append_claim_to_buffer"
                ).inc()
                if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                    self.flush_commit_buffer()

        except Exception as e:
            logging.error(f"Failed claim {record.claim_id}: {str(e)}")
            beam.metrics.Metrics.counter("process_paper_records/process", "error").inc()

        yield


def run_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    search_env: SearchEnv,
    search_index_id: str,
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

    search = ElasticClient(search_env)
    claim_index = ClaimIndex(search, search_index_id)
    if not claim_index.exists():
        logging.error(f"Failed to update embeddings: ES index does not exist: {search_index_id}")
        return

    with beam.Pipeline(options=pipeline_options) as p:
        (
            p
            | "ListClaimFeatureRecords" >> beam.Create(input_patterns)
            | "ReadFeatures" >> beam.io.parquetio.ReadAllFromParquet()
            | "ConvertToRecord" >> beam.Map(lambda x: ClaimEmbedding(**x))
            | "AddEmbeddingsToClaims"
            >> beam.ParDo(
                AddEmbeddingsToClaims(
                    dry_run=dry_run,
                    search_env=search_env,
                    project_id=project_id,
                    search_index_id=search_index_id,
                )
            )
        )
