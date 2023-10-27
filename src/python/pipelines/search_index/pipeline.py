import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
import apache_beam.io.textio as textio  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from claim_pb2 import ClaimNamespace
from common.beam.model_outputs import ModelOutput, read_qualifying_model_outputs_from_parquet
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.search.async_claim_index import AsyncClaimIndex
from common.search.claim_index import (
    CLAIM_INDEX_FIELD_TITLE_EMBEDDING,
    ClaimIndex,
    claim_to_document,
)
from common.search.claim_util import generate_claim
from common.search.connect import ElasticClient, SearchEnv
from common.storage.datasets import extract_search_index_id
from elasticsearch.helpers import streaming_bulk
from google.protobuf.json_format import MessageToJson

WITH_SPLIT_TITLE_EMBEDDING = True

LOG_FAILURE_MESSAGES_TO_RERUN = [
    "Connection timed out",
    "Connection timeout caused by",
]


@dataclass(frozen=True)
class PopulateSearchIndexResult(PipelineResult):
    paper_id: int
    claim: Optional[str]
    search_index_id: str
    dry_run: bool


class PopulateSearchIndex(beam.DoFn):
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

    def process(self, model_output: ModelOutput) -> Iterator[PopulateSearchIndexResult]:
        paper_id = model_output.paper_id
        try:
            paper = self.papers.read_by_id(paper_id)
            if not paper:
                raise ValueError("Failed to find paper for id {paper_id}")

            claim = generate_claim(
                embedding_model=self.claim_index.embedding_model,
                namespace=ClaimNamespace.EXTRACTED_FROM_PAPER,
                display_text=model_output.modified_claim,
                original_text=model_output.sentence,
                probability=model_output.claim_probability,
                paper=paper,
                with_split_title_embedding=WITH_SPLIT_TITLE_EMBEDDING,
            )
            search_index_document = claim_to_document(
                claim,
                with_split_title_embedding=WITH_SPLIT_TITLE_EMBEDDING,
            )
            document_dict = search_index_document.dict()
            if not WITH_SPLIT_TITLE_EMBEDDING:
                document_dict.pop(CLAIM_INDEX_FIELD_TITLE_EMBEDDING)
            self.commit_buffer.append(
                {
                    "_index": self.claim_index.name,
                    "_id": claim.id,
                    "_source": document_dict,
                }
            )

            if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                self.flush_commit_buffer()

            yield PopulateSearchIndexResult(
                paper_id=paper_id,
                claim=MessageToJson(claim, preserving_proto_field_name=True),
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            logging.error(e)
            yield PopulateSearchIndexResult(
                paper_id=paper_id,
                claim=None,
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


@dataclass(frozen=True)
class PaperIdPairedData:
    model_outputs: list[ModelOutput]
    log_results: list[PopulateSearchIndexResult]


class FilterPairedModelOutputs(beam.DoFn):
    """
    Generates an entry for all sitemap levels for a single claim.
    """

    def process(self, record: Any) -> Iterator[ModelOutput]:
        _, paired_data = record
        data = PaperIdPairedData(**paired_data)
        if len(data.log_results) > 0:
            for model_output in data.model_outputs:
                yield model_output


def _select_connection_failures_logs(log_result: PopulateSearchIndexResult) -> bool:
    if log_result.success:
        return False
    for message in LOG_FAILURE_MESSAGES_TO_RERUN:
        if log_result.message and log_result.message.startswith(message):
            return True
    return False


def filter_to_process_log_failures_only(
    p: beam.Pipeline,
    model_outputs: beam.PCollection[ModelOutput],
    input_logs_file_pattern: Optional[str],
) -> beam.PCollection[ModelOutput]:
    """
    Optionally filters the set of model outputs to add to the search index
    by an existing logs file failures.
    """

    if input_logs_file_pattern is None:
        return model_outputs

    failed_paper_id_pairs = (
        p
        | "ReadLogsFilesByLine" >> textio.ReadFromText(input_logs_file_pattern)
        | "ConvertLogToDataclass" >> beam.Map(lambda x: PopulateSearchIndexResult(**json.loads(x)))
        | "FilterForFailureWithMessage" >> beam.Filter(_select_connection_failures_logs)
        | "PairLogResultToPaperId" >> beam.Map(lambda x: (x.paper_id, x))
    )
    model_output_pairs = model_outputs | "PairModelOutputToPaperId" >> beam.Map(
        lambda x: (x.paper_id, x)
    )

    filtered_model_outputs = (
        (
            {
                "model_outputs": model_output_pairs,
                "log_results": failed_paper_id_pairs,
            }
        )
        | "GroupPairsByPaperId" >> beam.CoGroupByKey()
        | "FilterForUnpaired" >> beam.ParDo(FilterPairedModelOutputs())
        | "ReshuffleModelOutputsForFanout" >> beam.transforms.util.Reshuffle()
    )
    return filtered_model_outputs


def run_search_index_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    search_env: SearchEnv,
    input_file_pattern: str,
    input_logs_file_with_failures: Optional[str],
    add_to_existing_search_index_id: Optional[str],
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    search_index_id = add_to_existing_search_index_id
    if search_index_id is None:
        search_index_id = extract_search_index_id(input_file_pattern, config.timestamp)
        search = ElasticClient(search_env)
        claim_index = ClaimIndex(search, search_index_id)
        if claim_index.exists():
            print("ERROR: Claim index already exists")
            return

        if not dry_run:
            claim_index.create()

    with beam.Pipeline(options=pipeline_options) as p:
        all_model_outputs = read_qualifying_model_outputs_from_parquet(p, input_file_pattern)
        model_outputs = filter_to_process_log_failures_only(
            p, all_model_outputs, input_logs_file_with_failures
        )
        results = model_outputs | "PopulateSearchIndex" >> beam.ParDo(
            PopulateSearchIndex(
                dry_run=dry_run,
                search_env=search_env,
                db_env=db_env,
                project_id=project_id,
                search_index_id=search_index_id,
            )
        )

        write_pipeline_results(config.results_file, results)
