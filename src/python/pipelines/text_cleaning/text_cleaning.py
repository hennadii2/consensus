import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, List, Optional, Tuple

import apache_beam as beam  # type: ignore
import apache_beam.io.textio as textio  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.papers import read_papers_with_status
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.ingestion.extract import extract_metadata_and_abstract, filter_metadata_for_product
from common.storage.connect import StorageClient, StorageEnv
from common.storage.paper_data import write_clean_abstract
from common.text_cleaning.base_text_cleaner import BaseTextCleaner
from paper_metadata_pb2 import PaperProvider
from paper_pb2 import Paper, PaperStatus


@dataclass(frozen=True)
class PaperToRawAbstractPair:
    paper: List[Paper]
    abstract: List[Optional[str]]


@dataclass(frozen=True)
class WriteCleanAbstractsResult(PipelineResult):
    paper_id: str
    clean_data_url: Optional[str]
    dry_run: bool


class WriteCleanAbstracts(beam.DoFn):
    """
    DoFn to write clean abstracts to blob store and update papers in DB with
    clean_data_url and CLEANED status.
    """

    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        storage_env: StorageEnv,
        project_id: str,
        job_name: str,
        timestamp: datetime,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.storage_env = storage_env
        self.project_id = project_id
        self.job_name = job_name
        self.timestamp = timestamp

    def setup(self):
        # Set GCLOUD_PROJECT_ID in worker to enable access to secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.base_text_cleaner = BaseTextCleaner()
        self.storage_client = StorageClient(self.storage_env)
        if not self.dry_run:
            connection = MainDbClient(self.db_env)
            self.db = Papers(connection)
            self.commit_batch_count = 0

    def teardown(self):
        if not self.dry_run:
            self.db.connection.commit()
            self.db.connection.close()

    def process(self, pair: PaperToRawAbstractPair) -> Iterator[WriteCleanAbstractsResult]:
        if len(pair.paper) != 1 or len(pair.abstract) != 1:
            yield WriteCleanAbstractsResult(
                paper_id="empty",
                clean_data_url=None,
                dry_run=self.dry_run,
                success=False,
                message="Bad pipeline pair input, "
                + f"found {len(pair.paper)} papers and {len(pair.abstract)} abstracts.",
            )
            return
        paper = pair.paper[0]
        abstract = pair.abstract[0]

        if abstract is None:
            yield WriteCleanAbstractsResult(
                paper_id="empty",
                clean_data_url=None,
                dry_run=self.dry_run,
                success=False,
                message="Abstract is none",
            )
            return

        try:
            filter_metadata_for_product(paper.metadata)
            # TODO(meganvw,bnebeker): For first release of product we are not
            # cleaning the text to simplify. Reenable once ready.
            # clean_abstract = self.base_text_cleaner.clean_text(abstract)
            clean_abstract = abstract
            clean_data_url = "unset for dry run"
            if not self.dry_run:
                clean_data_url = write_clean_abstract(
                    client=self.storage_client,
                    clean_abstract=clean_abstract,
                    paper=paper,
                    timestamp=self.timestamp,
                )
                self.db.update_clean_data_url(
                    paper_id=paper.id,
                    clean_data_url=clean_data_url,
                    abstract=abstract,
                    job_name=self.job_name,
                    timestamp=self.timestamp,
                    commit=False,
                )

                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db.connection.commit()
                    self.commit_batch_count = 0

            yield WriteCleanAbstractsResult(
                paper_id=str(paper.id),
                clean_data_url=clean_data_url,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield WriteCleanAbstractsResult(
                paper_id=str(paper.id),
                clean_data_url=None,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


@dataclass(frozen=True)
class ProviderIdKey:
    provider_id: str
    raw_data_url: str


def raw_data_to_tuple(record: Any) -> Tuple[ProviderIdKey, Optional[str]]:
    filename, text = record
    # TODO(meganvw): We should get the provider dynamically here.
    metadata, abstract = extract_metadata_and_abstract(PaperProvider.SEMANTIC_SCHOLAR, text)
    pair_key = ProviderIdKey(provider_id=metadata.provider_id, raw_data_url=filename)
    return (pair_key, abstract)


def paper_to_tuple(paper: Paper) -> Tuple[ProviderIdKey, Paper]:
    pair_key = ProviderIdKey(
        provider_id=paper.metadata.provider_id, raw_data_url=paper.raw_data_url
    )
    return (pair_key, paper)


def run_text_cleaning_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    storage_env: StorageEnv,
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
        paper_protos = read_papers_with_status(
            p,
            db_env,
            project_id,
            PaperStatus.Status.INGESTED,
        )

        # Raw abstracts are stored in batch archived files, so we get the set
        # of their unique raw_data_urls, read all raw abstracts from the batch
        # files, and then re-pair the raw text with its corresponding DB paper
        # by matching ProviderIdKeys.

        # Pair provider IDs to raw paper abstracts
        raw_abstract_pairs = (
            paper_protos
            | "GetRawDataUrl" >> beam.Map(lambda paper: paper.raw_data_url)
            | "DedupRawDataUrls" >> beam.Distinct()
            | "ReadRawDataUrlsByLine" >> textio.ReadAllFromText(with_filename=True)
            | "PairProviderIdKeyWithRawText" >> beam.Map(raw_data_to_tuple)
        )

        # Pair provider IDs to papers
        paper_proto_pairs = paper_protos | "PairProviderIdKeyWithPaper" >> beam.Map(paper_to_tuple)

        # Group paper IDs with their cleaned abstracts and write to blob store
        results = (
            (
                {
                    "paper": paper_proto_pairs,
                    "abstract": raw_abstract_pairs,
                }
            )
            | "GroupPairsByProviderIdKey" >> beam.CoGroupByKey()
            | "ExtractPaperAndAbstractsDict" >> beam.Map(lambda x: PaperToRawAbstractPair(**x[1]))
            # Abstracts may be unpaired if they were skipped during DB ingestion.
            | "FilterUnpairedAbstracts" >> beam.Filter(lambda x: len(x.paper) > 0)
            | "WriteCleanAbastractsToBlobAndUpdateDb"
            >> beam.ParDo(
                WriteCleanAbstracts(
                    dry_run=dry_run,
                    db_env=db_env,
                    storage_env=storage_env,
                    project_id=project_id,
                    job_name=config.job_name,
                    timestamp=config.timestamp,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
