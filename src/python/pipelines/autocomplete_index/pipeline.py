import logging
import os
from dataclasses import asdict, dataclass
from typing import Any, Iterator

import apache_beam as beam  # type: ignore
import pandas as pd
from apache_beam.dataframe.convert import to_pcollection  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId, access_secret
from common.models.offensive_query_classifier import (
    initialize_offensive_query_classifier,
    is_query_offensive,
)
from common.search.autocomplete_index import (
    AutocompleteIndex,
    query_to_document,
    query_to_document_id,
)
from common.search.connect import ElasticClient, SearchEnv
from elasticsearch.helpers import streaming_bulk

SELECTED_ROW_SCHEMA = {"Result": "result", "Claim": "claim"}


@dataclass(frozen=True)
class GeneratedQueriesData:
    claim: str
    query: str


def csv_row_to_dataclass(df_row: Any) -> GeneratedQueriesData:
    """
    Converts generated queries raw row data to dataclasses with validation.
    """
    result = df_row.result
    if result is not None:
        result = result.strip()
    return GeneratedQueriesData(query=result, claim=df_row.claim)


@dataclass(frozen=True)
class WriteToAutocompleteSearchIndexResult(PipelineResult):
    query: str
    claim: str
    search_index_id: str
    dry_run: bool


class WriteToAutocompleteSearchIndex(beam.DoFn):
    """
    Writes autocomplete queries to the search index.
    """

    # Number of records to write to search index in one commit
    MAX_COMMIT_BATCH_COUNT = 500

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

        hf_key = access_secret(SecretId.HUGGING_FACE_API_KEY)
        self.offensive_query_classifier = initialize_offensive_query_classifier(hf_api_key=hf_key)

        search = ElasticClient(self.search_env)
        self.autocomplete_index = AutocompleteIndex(search, self.search_index_id)

        self.commit_buffer = []

    def flush_commit_buffer(self):
        failures = 0
        if not self.dry_run:
            for ok, action in streaming_bulk(
                client=self.autocomplete_index.es,
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
        self.autocomplete_index.es.close()

    def process(
        self, data: GeneratedQueriesData
    ) -> Iterator[WriteToAutocompleteSearchIndexResult]:
        try:
            is_offensive = is_query_offensive(
                model=self.offensive_query_classifier,
                query=data.query,
            )
            if is_offensive:
                raise ValueError("Failed to process: query is offensive")

            self.commit_buffer.append(
                {
                    "_index": self.autocomplete_index.name,
                    "_id": query_to_document_id(data.query),
                    "_source": asdict(query_to_document(data.query)),
                }
            )

            if len(self.commit_buffer) >= self.MAX_COMMIT_BATCH_COUNT:
                self.flush_commit_buffer()

            yield WriteToAutocompleteSearchIndexResult(
                query=data.query,
                claim=data.claim,
                search_index_id=self.search_index_id,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            logging.error(e)
            yield WriteToAutocompleteSearchIndexResult(
                query=data.query,
                claim=data.claim,
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
    search_env: SearchEnv,
    input_path: str,
) -> None:
    pipeline_options = PipelineOptions(
        beam_args,
        runner=runner,
        job_name=config.job_name,
        temp_location=config.temp_dir,
        max_num_workers=config.max_num_workers,
    )
    pipeline_options.view_as(SetupOptions).save_main_session = True

    search_index_id = "suggester-dev-230222-2"

    es = ElasticClient(search_env)
    autocomplete_index = AutocompleteIndex(es, search_index_id)
    if not autocomplete_index.exists() and not dry_run:
        autocomplete_index.create()

    # Read sciscore data into memory, data is not too large
    queries_df = pd.read_csv(filepath_or_buffer=input_path)

    # Select only columns we'll use, and rename so we don't hit errors in beam
    # due to spaces / malformed column names
    queries_df = queries_df[list(SELECTED_ROW_SCHEMA.keys())]
    queries_df.rename(columns=SELECTED_ROW_SCHEMA, inplace=True)

    with beam.Pipeline(options=pipeline_options) as p:
        pcollection = to_pcollection(queries_df, pipeline=p)
        results = (
            pcollection
            | "ConvertToDataclass" >> beam.Map(csv_row_to_dataclass)
            | "WriteToAutocompleteSearchIndex"
            >> beam.ParDo(
                WriteToAutocompleteSearchIndex(
                    dry_run=dry_run,
                    search_index_id=search_index_id,
                    search_env=search_env,
                    project_id=project_id,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
