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
from common.beam.records.abstract_takeaways_record import AbstractTakeawayRecord
from common.config.secret_manager import SecretId
from common.db.abstract_takeaways import AbstractTakeaways, TakeawayMetrics
from common.db.connect import DbEnv, MainDbClient


@dataclass(frozen=True)
class WriteToDbResult(PipelineResult):
    dry_run: bool


class WriteAbstractTakeawaysToDb(beam.DoFn):
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
            self.abstract_takeaways = AbstractTakeaways(connection=self.db_connection)
            self.commit_batch_count = 0

    def finish_bundle(self):
        if not self.dry_run:
            self.db_connection.commit()
            beam.metrics.Metrics.counter("process_abstract_takeaways/process", "commit").inc(
                self.commit_batch_count
            )

    def teardown(self):
        if not self.dry_run:
            self.db_connection.close()

    def process(self, record: AbstractTakeawayRecord) -> Iterator[WriteToDbResult]:
        try:
            beam.metrics.Metrics.counter(
                "process_abstract_takeaways/process", "process_takeaway"
            ).inc()
            if not self.dry_run:
                metrics = TakeawayMetrics(
                    takeaway_to_title_abstract_r1r=record.takeaway_to_title_abstract_r1r,
                    takeaway_length=record.takeaway_length,
                    takeaway_distinct_pct=record.takeaway_distinct_pct,
                    takeaway_non_special_char_pct=record.takeaway_non_special_char_pct,
                    abstract_length=record.abstract_length,
                    abstract_distinct_pct=record.abstract_distinct_pct,
                    abstract_non_special_char_pct=record.abstract_non_special_char_pct,
                )
                self.abstract_takeaways.write_takeaway(
                    paper_id=record.paper_id,
                    takeaway=record.abstract_takeaway,
                    metrics=metrics,
                    job_name=self.job_name,
                    timestamp=self.timestamp,
                    commit=False,
                )
                beam.metrics.Metrics.counter(
                    "process_paper_records/process", "write_takeaway"
                ).inc()

                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db_connection.commit()
                    beam.metrics.Metrics.counter("process_paper_records/process", "commit").inc(
                        self.commit_batch_count
                    )
                    self.commit_batch_count = 0
            else:
                beam.metrics.Metrics.counter(
                    "process_abstract_takeaways/process", "skip_write_for_dry_run"
                ).inc()

        except Exception as e:
            logging.error(str(e))
            beam.metrics.Metrics.counter("process_paper_records/process", "error").inc()
            yield WriteToDbResult(
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
        results = (
            p
            | "ListPaperFeatureRecords" >> beam.Create(input_patterns)
            | "ReadFeatures" >> beam.io.parquetio.ReadAllFromParquet()
            | "ConvertToRecord" >> beam.Map(lambda x: AbstractTakeawayRecord(**x))
            | "WriteAbstractTakeawaysToDb"
            >> beam.ParDo(
                WriteAbstractTakeawaysToDb(
                    dry_run=dry_run,
                    db_env=db_env,
                    project_id=project_id,
                    job_name=config.job_name,
                    timestamp=config.timestamp,
                )
            )
        )

        write_pipeline_results(config.results_file, results)
