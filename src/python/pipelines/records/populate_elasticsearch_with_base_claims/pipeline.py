import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from claim_pb2 import ClaimNamespace
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.beam.records.claim_feature_record import (
    ClaimFeatureRecord,
    read_qualifying_claims_from_parquet,
)
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.records.paper_records import PaperRecords
from common.search.claim_index import ClaimIndex, claim_to_document
from common.search.claim_util import generate_base_claim
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import streaming_bulk


@dataclass(frozen=True)
class PopulateBaseClaimsResult(PipelineResult):
    paper_id: str
    claim: Optional[str]
    search_index_id: str
    dry_run: bool


class PopulateBaseClaims(beam.DoFn):
    """
    DoFn to write claims that meet a threshold to a new index in elasticsearch.
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

        self.db_connection = MainDbClient(self.db_env)
        self.paper_records = PaperRecords(self.db_connection)

        if not self.dry_run:
            self.es_connection = ElasticClient(self.search_env)
            self.claim_index = ClaimIndex(self.es_connection, self.search_index_id)
            self.commit_buffer = []

    def flush_commit_buffer(self):
        if not self.dry_run:
            failures = 0
            for ok, action in streaming_bulk(
                client=self.claim_index.es,
                actions=self.commit_buffer,
                max_retries=3,
                yield_ok=False,
                raise_on_error=False,
                raise_on_exception=False,
            ):
                if not ok:
                    failures = failures + 1
                    logging.error(action)
                    if failures == 1:
                        logging.info(f"commit example: {self.commit_buffer[0]}")

            logging.info(f"Flush commit buffer failures: {failures}/{len(self.commit_buffer)}")
            beam.metrics.Metrics.counter(
                "process_paper_records/process", "flush_commit_buffer_failures"
            ).inc(failures)
            beam.metrics.Metrics.counter(
                "process_paper_records/process", "flush_commit_buffer_successes"
            ).inc(len(self.commit_buffer) - failures)
            del self.commit_buffer
            self.commit_buffer = []

    def finish_bundle(self):
        if not self.dry_run:
            self.flush_commit_buffer()

    def teardown(self):
        self.db_connection.close()
        if not self.dry_run:
            self.es_connection.close()

    def process(self, record: ClaimFeatureRecord) -> Iterator[PopulateBaseClaimsResult]:
        try:
            paper_record = self.paper_records.read_by_id(
                paper_id=record.paper_id,
                active_only=True,
                max_version=None,
            )
            if paper_record is None:
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "missing_paper_record"
                ).inc()
                raise ValueError("missing_paper_record")

            claim = generate_base_claim(
                namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                display_text=(
                    record.enhanced_claim
                    if record.enhanced_claim is not None
                    else record.modified_claim
                ),
                original_text=record.sentence,
                probability=record.claim_probability,
                paper_id=record.paper_id,
                paper_metadata=paper_record.metadata,
                is_enhanced=record.enhanced_claim is not None,
            )
            search_index_document = claim_to_document(
                claim,
                with_split_title_embedding=True,
                allow_empty_embeddings=True,
            )
            document_dict = search_index_document.dict()

            beam.metrics.Metrics.counter("process_paper_records/process", "generated_claim").inc()
            if not self.dry_run:
                self.commit_buffer.append(
                    {
                        "_index": self.claim_index.name,
                        "_id": claim.id,
                        "_source": document_dict,
                    }
                )
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "append_claim_to_buffer"
                ).inc()
                if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                    self.flush_commit_buffer()

        except Exception as e:
            logging.error(e)
            beam.metrics.Metrics.counter("process_paper_records/process", "error").inc()
            yield PopulateBaseClaimsResult(
                paper_id=record.paper_id,
                claim=None,
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
        results = read_qualifying_claims_from_parquet(
            p, input_patterns=input_patterns
        ) | "PopulateBaseClaims" >> beam.ParDo(
            PopulateBaseClaims(
                dry_run=dry_run,
                search_env=search_env,
                db_env=db_env,
                project_id=project_id,
                search_index_id=search_index_id,
            )
        )

        write_pipeline_results(config.results_file, results)
