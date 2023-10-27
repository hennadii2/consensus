import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.records.embedding_record import TitleEmbedding
from common.config.secret_manager import SecretId
from common.search.claim_index import ClaimIndex
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import scan, streaming_bulk


@dataclass(frozen=True)
class RecordWithClaimId:
    claim_id: str
    record: TitleEmbedding


class BatchReadClaimIds(beam.DoFn):
    """
    DoFn to retrieve claim ids from an Elasticsearch index by paper_id.
    """

    # Number of records to read from search index in one query
    MAX_SCROLL_SIZE = 250

    def __init__(
        self,
        search_env: SearchEnv,
        project_id: str,
        search_index_id: str,
    ):
        self.search_env = search_env
        self.project_id = project_id
        self.search_index_id = search_index_id
        # Window is required for finish_bundle to emit values
        self.window = beam.transforms.window.GlobalWindow()

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.es_connection = ElasticClient(self.search_env)
        self.claim_index = ClaimIndex(self.es_connection, self.search_index_id)

        self.paper_ids_read_buffer = []
        self.record_dict: dict[str, TitleEmbedding] = {}

    def teardown(self):
        self.es_connection.close()

    def finish_bundle(self):
        for result in self.scan_for_claim_ids():
            yield beam.utils.windowed_value.WindowedValue(
                value=result,
                timestamp=0,
                windows=[self.window],
            )

    def scan_for_claim_ids(self):
        beam.metrics.Metrics.counter("read_claim_ids/bulk_read", "scan_claim_ids_calls").inc()

        if len(self.paper_ids_read_buffer) <= 0:
            # Scan fails for 0 length, so skip
            return

        query = {
            "_source": False,
            "query": {
                "terms": {
                    "paper_id": self.paper_ids_read_buffer,
                },
            },
            "docvalue_fields": ["paper_id"],
        }
        for hit in scan(
            client=self.claim_index.es,
            index=self.claim_index.name,
            query=query,
            scroll="5m",
            raise_on_error=False,
            size=len(self.paper_ids_read_buffer),
        ):
            claim_id = hit["_id"]
            # docvalue fields always return an array, so access first element
            paper_id = hit["fields"]["paper_id"][0]
            output = RecordWithClaimId(claim_id=claim_id, record=self.record_dict[paper_id])
            beam.metrics.Metrics.counter("read_claim_ids/bulk_read", "output_records").inc()
            yield output

        del self.paper_ids_read_buffer
        self.paper_ids_read_buffer = []

    def process(
        self, record: TitleEmbedding, window=beam.DoFn.WindowParam
    ) -> Iterator[RecordWithClaimId]:
        beam.metrics.Metrics.counter("read_claim_ids/bulk_read", "input_records").inc()
        self.window = window

        self.record_dict[record.paper_id] = record
        self.paper_ids_read_buffer.append(record.paper_id)
        if len(self.paper_ids_read_buffer) >= self.MAX_SCROLL_SIZE:
            for result in self.scan_for_claim_ids():
                yield result


class BatchWriteTitleEmbeddingsToClaims(beam.DoFn):
    """
    DoFn to write title embeddings to elasticsearch.
    """

    # Number of records to write to search index in one commit
    MAX_COMMIT_BATCH_COUNT = 1000

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
                    "write_title_embeddings/process", "flush_commit_buffer_failures"
                ).inc(failures)
                beam.metrics.Metrics.counter(
                    "write_title_embeddings/process", "flush_commit_buffer_successes"
                ).inc(len(self.commit_buffer) - failures)
            except Exception as e:
                logging.error(f"Failed commit: {e}")
                beam.metrics.Metrics.counter(
                    "write_title_embeddings/process", "commit_failure"
                ).inc(len(self.commit_buffer))

            del self.commit_buffer
            self.commit_buffer = []

    def finish_bundle(self):
        if not self.dry_run:
            self.flush_commit_buffer()

    def teardown(self):
        if not self.dry_run:
            self.es_connection.close()

    def process(self, record_with_claim_id: RecordWithClaimId) -> Iterator[None]:
        try:
            beam.metrics.Metrics.counter(
                "write_title_embeddings/process", "process_embedding"
            ).inc()
            if not self.dry_run:
                self.commit_buffer.append(
                    {
                        "_index": self.claim_index.name,
                        "_id": record_with_claim_id.claim_id,
                        "_op_type": "update",
                        "doc": {
                            "title_embedding": record_with_claim_id.record.embeddings,
                        },
                    }
                )
                beam.metrics.Metrics.counter(
                    "write_title_embeddings/process", "append_claim_to_buffer"
                ).inc()

                if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                    self.flush_commit_buffer()
            else:
                logging.info(record_with_claim_id)

        except Exception as e:
            logging.error(f"Failed paper {record_with_claim_id.record.paper_id}: {str(e)}")
            beam.metrics.Metrics.counter("write_title_embeddings/process", "error").inc()

        # yield nothing
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
        num_workers=config.max_num_workers,
        autoscaling_algorithm=None,
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
            | "ConvertToRecord" >> beam.Map(lambda x: TitleEmbedding(**x))
            | "BatchReadClaimIds"
            >> beam.ParDo(
                BatchReadClaimIds(
                    search_env=search_env,
                    project_id=project_id,
                    search_index_id=search_index_id,
                )
            )
            | "BatchWriteTitleEmbeddingsToClaims"
            >> beam.ParDo(
                BatchWriteTitleEmbeddingsToClaims(
                    dry_run=dry_run,
                    search_env=search_env,
                    project_id=project_id,
                    search_index_id=search_index_id,
                )
            )
        )
