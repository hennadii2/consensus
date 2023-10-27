from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.beam.records.base_record import RecordStatus, extract_version_from_input_file
from common.beam.records.paper_feature_record import PaperFeatureRecord
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.records.abstract_records import AbstractRecords
from common.db.records.paper_records import PaperRecords
from common.storage.connect import StorageEnv, init_storage_client
from common.storage.paper_data import write_clean_abstract_to_v2_storage

FEATURE_GCS_PREFIX_TO_PARSE_VERSION = "gs://consensus-paper-data/features/papers/"


@dataclass(frozen=True)
class PaperFeatureRecordWithFilename:
    filename: str
    record: PaperFeatureRecord


@dataclass(frozen=True)
class WriteToDbAndStorageResult(PipelineResult):
    dry_run: bool


class WriteToDbAndStorage(beam.DoFn):
    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        storage_env: StorageEnv,
        job_name: str,
        project_id: str,
        timestamp: datetime,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.storage_env = storage_env
        self.job_name = job_name
        self.project_id = project_id
        self.timestamp = timestamp

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        if not self.dry_run:
            os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id
            self.storage_client = init_storage_client(self.storage_env)

            self.db_connection = MainDbClient(self.db_env)
            self.paper_records_db = PaperRecords(connection=self.db_connection)
            self.abstract_records_db = AbstractRecords(connection=self.db_connection)
            self.commit_batch_count = 0

    def finish_bundle(self):
        if not self.dry_run:
            self.db_connection.commit()
            beam.metrics.Metrics.counter("process_paper_records/process", "commit").inc(
                self.commit_batch_count
            )

    def teardown(self):
        if not self.dry_run:
            self.db_connection.close()

    def process(
        self, record_with_filename: PaperFeatureRecordWithFilename
    ) -> Iterator[WriteToDbAndStorageResult]:
        try:
            record = record_with_filename.record
            if record.status == RecordStatus.ERROR:
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "skipping_paper_with_error"
                ).inc()
                return

            # Version is derived from directory structure of the input file
            # These versions are requried to be timestamp prefixed for accurate
            # versioning of records in our database.
            version = extract_version_from_input_file(
                input_file=record_with_filename.filename,
                expected_gcs_prefix=FEATURE_GCS_PREFIX_TO_PARSE_VERSION,
            )
            beam.metrics.Metrics.counter("process_paper_records/process", "process_paper").inc()
            if not self.dry_run:
                wrote_to_db = False
                if record.metadata:
                    # TODO(meganvw): Lookup existing record and skip metadata
                    # write if paper is unchanged.

                    self.paper_records_db.write_record(
                        paper_id=record.paper_id,
                        version=version,
                        metadata=record.metadata,
                        status=record.status,
                        status_msg=record.status_msg,
                        input_data_hash=record.input_data_hash,
                        method_version_hash=record.method_version_hash,
                        job_name=self.job_name,
                        timestamp=self.timestamp,
                        commit=False,
                    )
                    beam.metrics.Metrics.counter(
                        "process_paper_records/process", "write_paper"
                    ).inc()
                    wrote_to_db = True

                if record.abstract:
                    # TODO(meganvw): Lookup existing record and skip abstract
                    # write if paper is unchanged.

                    # Write to storage
                    clean_data_url = write_clean_abstract_to_v2_storage(
                        client=self.storage_client,
                        clean_abstract=record.abstract,
                        paper_id=record.paper_id,
                        timestamp=self.timestamp,
                    )
                    self.abstract_records_db.write_record(
                        paper_id=record.paper_id,
                        version=version,
                        gcs_abstract_url=clean_data_url,
                        status=record.status,
                        status_msg=record.status_msg,
                        input_data_hash=record.input_data_hash,
                        method_version_hash=record.method_version_hash,
                        job_name=self.job_name,
                        timestamp=self.timestamp,
                        commit=False,
                    )
                    beam.metrics.Metrics.counter(
                        "process_paper_records/process", "write_abstracts"
                    ).inc()
                    wrote_to_db = True

                if wrote_to_db:
                    self.commit_batch_count += 1
                    if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                        self.db_connection.commit()
                        beam.metrics.Metrics.counter(
                            "process_paper_records/process", "commit"
                        ).inc(self.commit_batch_count)
                        self.commit_batch_count = 0

        except Exception as e:
            logging.error(str(e))
            beam.metrics.Metrics.counter("process_paper_records/process", "error").inc()
            yield WriteToDbAndStorageResult(
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
    storage_env: StorageEnv,
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

    project_id = project_id
    with beam.Pipeline(options=pipeline_options) as p:
        results = (
            p
            | "ListPaperFeatureRecords" >> beam.Create(input_patterns)
            | "ReadFeatures" >> beam.io.parquetio.ReadAllFromParquet(with_filename=True)
            | "ConvertToRecord"
            >> beam.Map(
                lambda x: PaperFeatureRecordWithFilename(
                    filename=x[0],
                    record=PaperFeatureRecord(**x[1]),
                )
            )
            | "WriteToDbAndStorage"
            >> beam.ParDo(
                WriteToDbAndStorage(
                    dry_run=dry_run,
                    db_env=db_env,
                    storage_env=storage_env,
                    job_name=config.job_name,
                    project_id=project_id,
                    timestamp=config.timestamp,
                )
            )
        )

        write_pipeline_results(
            output_file=config.results_file,
            results=results,
            individual_failures_only=True,
            custom_filter_for_individual_results=None,
        )
