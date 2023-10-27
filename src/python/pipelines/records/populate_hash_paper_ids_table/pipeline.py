from __future__ import annotations

import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.beam.records.full_merged_paper_feature_record import (
    FullMergedPaperFeatureRecord,
    read_qualifying_merged_paper_feature_records_from_parquet,
)
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.hash_paper_ids import HashPaperIds
from common.search.paper_util import PaperIdProvider, generate_hash_paper_id


@dataclass(frozen=True)
class WriteToDbResult(PipelineResult):
    dry_run: bool
    paper_id: str
    hash_paper_id: Optional[str]


class WriteHashPaperIdsToDb(beam.DoFn):
    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 1500

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        job_name: str,
        project_id: str,
        timestamp: datetime,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.job_name = job_name
        self.project_id = project_id
        self.timestamp = timestamp

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        if not self.dry_run:
            os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

            self.db_connection = MainDbClient(self.db_env)
            self.db = HashPaperIds(connection=self.db_connection)
            self.commit_batch_count = 0

    def finish_bundle(self):
        if not self.dry_run:
            self.db_connection.commit()
            beam.metrics.Metrics.counter("process_hash_paper_id/process", "commit").inc(
                self.commit_batch_count
            )

    def teardown(self):
        if not self.dry_run:
            self.db_connection.close()

    def process(self, record: FullMergedPaperFeatureRecord) -> Iterator[WriteToDbResult]:
        hash_paper_id = None
        try:
            beam.metrics.Metrics.counter("process_hash_paper_id/process", "process_record").inc()
            hash_paper_id = generate_hash_paper_id(PaperIdProvider.S2, record.paper_id)
            if not self.dry_run:
                self.db.write_mapping(
                    paper_id=record.paper_id,
                    hash_paper_id=hash_paper_id,
                    job_name=self.job_name,
                    timestamp=self.timestamp,
                    commit=False,
                )
                beam.metrics.Metrics.counter("process_hash_paper_id/process", "write_to_db").inc()

                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db_connection.commit()
                    beam.metrics.Metrics.counter("process_paper_records/process", "commit").inc(
                        self.commit_batch_count
                    )
                    self.commit_batch_count = 0
            else:
                beam.metrics.Metrics.counter(
                    "process_hash_paper_id/process", "skip_write_for_dry_run"
                ).inc()

        except Exception as e:
            logging.error(str(e))
            beam.metrics.Metrics.counter("process_paper_records/process", "error").inc()
            yield WriteToDbResult(
                paper_id=record.paper_id,
                hash_paper_id=hash_paper_id,
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
        results = read_qualifying_merged_paper_feature_records_from_parquet(
            p, input_patterns=input_patterns
        ) | "WriteHashPaperIdsToDb" >> beam.ParDo(
            WriteHashPaperIdsToDb(
                dry_run=dry_run,
                db_env=db_env,
                project_id=project_id,
                job_name=config.job_name,
                timestamp=config.timestamp,
            )
        )

        write_pipeline_results(config.results_file, results)
