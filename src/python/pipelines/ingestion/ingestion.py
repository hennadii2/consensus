import os
from dataclasses import dataclass
from typing import Any, Iterator

import apache_beam as beam  # type: ignore
import apache_beam.io.textio as textio  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.ingestion.extract import extract_metadata, filter_metadata_for_ingestion
from paper_metadata_pb2 import PaperProvider


@dataclass(frozen=True)
class IngestPaperDataResult(PipelineResult):
    record_id: str
    record_path: str
    dry_run: bool


class IngestPaperData(beam.DoFn):
    """
    Beam DoFn to extract paper metadata from raw provider records
    and write the metadata to the DB.
    """

    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        job_name: str,
        project_id: str,
        provider: str,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.job_name = job_name
        self.project_id = project_id
        self.provider = provider

    def setup(self):
        self.db = None
        if not self.dry_run:
            # Add project ID to worker environment to allow connection to
            # secret manager
            os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id
            connection = MainDbClient(self.db_env)
            self.db = Papers(connection)
            self.commit_batch_count = 0

    def teardown(self):
        if not self.dry_run:
            self.db.connection.commit()
            self.db.connection.close()

    def process(self, record: Any) -> Iterator[IngestPaperDataResult]:
        filepath, text = record
        provider = PaperProvider.Value(self.provider)
        metadata = extract_metadata(provider, text)

        try:
            # Skip saving invalid metadata to the database
            filter_metadata_for_ingestion(metadata)

            if not self.dry_run:
                self.db.write_paper(
                    raw_data_url=filepath,
                    metadata=metadata,
                    provider_metadata={},
                    job_name=self.job_name,
                    timestamp=None,
                    commit=False,
                    update_if_exists=False,
                )

                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db.connection.commit()
                    self.commit_batch_count = 0

            yield IngestPaperDataResult(
                record_id=metadata.provider_id,
                record_path=filepath,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield IngestPaperDataResult(
                record_id=metadata.provider_id,
                record_path=filepath,
                dry_run=self.dry_run,
                success=False,
                message=str(e),
            )


def run_ingestion_pipeline(
    runner: str,
    project_id: str,
    beam_args: Any,
    config: PipelineConfig,
    dry_run: bool,
    db_env: DbEnv,
    input_dir: str,
    provider: str,
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
        results = (
            p
            | "ReadFilesByLine" >> textio.ReadFromTextWithFilename(input_dir)
            | "IngestPaperDataAndWriteToDb"
            >> beam.ParDo(
                IngestPaperData(
                    dry_run=dry_run,
                    db_env=db_env,
                    job_name=config.job_name,
                    project_id=project_id,
                    provider=provider,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
