import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from claim_pb2 import ClaimNamespace
from common.beam.model_outputs import ModelOutput, read_qualifying_model_outputs_from_parquet
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.search.async_claim_index import AsyncClaimIndex
from common.search.claim_index import ClaimIndex
from common.search.claim_util import generate_base_claim
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import streaming_bulk
from google.protobuf.json_format import MessageToJson

WITH_SPLIT_TITLE_EMBEDDING = True


@dataclass(frozen=True)
class DeleteSearchDocsResult(PipelineResult):
    paper_id: int
    claim: Optional[str]
    search_index_id: str
    dry_run: bool


class DeleteSearchDocs(beam.DoFn):
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

        db = MainDbClient(self.db_env)
        self.papers = Papers(db)

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
                if not ok:
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
        self.papers.connection.close()

    def process(self, model_output: ModelOutput) -> Iterator[DeleteSearchDocsResult]:
        paper_id = model_output.paper_id
        try:
            paper = self.papers.read_by_id(paper_id)
            if not paper:
                raise ValueError("Failed to find paper for id {paper_id}")

            claim = generate_base_claim(
                namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                display_text=model_output.modified_claim,
                original_text=model_output.sentence,
                probability=model_output.claim_probability,
                paper_id=paper.paper_id,
                paper_metadata=paper.metadata,
                is_enhanced=False,
            )
            self.commit_buffer.append(
                {
                    "_op_type": "delete",
                    "_index": self.claim_index.name,
                    "_id": claim.id,
                }
            )

            if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                self.flush_commit_buffer()

            yield DeleteSearchDocsResult(
                paper_id=paper_id,
                claim=MessageToJson(claim, preserving_proto_field_name=True),
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            logging.error(e)
            yield DeleteSearchDocsResult(
                paper_id=paper_id,
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
    search_index_id: str,
    input_file_pattern: str,
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
        print("ERROR: Claim index does not exist")
        return

    with beam.Pipeline(options=pipeline_options) as p:
        model_outputs = read_qualifying_model_outputs_from_parquet(p, input_file_pattern)
        results = model_outputs | "DeleteSearchDocs" >> beam.ParDo(
            DeleteSearchDocs(
                dry_run=dry_run,
                search_env=search_env,
                db_env=db_env,
                project_id=project_id,
                search_index_id=search_index_id,
            )
        )

        write_pipeline_results(config.results_file, results)
