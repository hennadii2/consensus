import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable, Iterator, Tuple

import apache_beam as beam  # type: ignore
import apache_beam.io.parquetio as parquetio  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId
from common.db.connect import DbEnv, MainDbClient
from common.db.paper_inferences import PaperInferences
from paper_inferences_pb2 import InferenceData, PaperInference


@dataclass(frozen=True)
class StudyType:
    paper_id: int
    probability: float
    prediction: str


def parquet_record_to_dataclass(record: Any) -> StudyType:
    prediction = record["study_type_prediction"]
    prediction = "None" if prediction is None else prediction.removesuffix("Bucket")
    return StudyType(
        paper_id=record["paper_id"],
        probability=max(record["study_type_probability"]),
        prediction=prediction.strip(),
    )


@dataclass(frozen=True)
class WriteToDbResult(PipelineResult):
    paper_id: int
    study_type: str
    dry_run: bool


class WriteToDb(beam.DoFn):
    # Number of records to write to DB in one commit
    MAX_COMMIT_BATCH_COUNT = 100

    def __init__(
        self,
        dry_run: bool,
        db_env: DbEnv,
        job_name: str,
        timestamp: datetime,
        project_id: str,
        source: str,
    ):
        self.dry_run = dry_run
        self.db_env = db_env
        self.job_name = job_name
        self.timestamp = timestamp
        self.project_id = project_id
        self.source = source

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        if not self.dry_run:
            self.db = MainDbClient(self.db_env)
            self.paper_inferences = PaperInferences(self.db)
            self.commit_batch_count = 0

    def finish_bundle(self):
        if not self.dry_run:
            self.db.commit()

    def teardown(self):
        if not self.dry_run:
            self.db.close()

    def process(self, record: Tuple[Any, Iterable[StudyType]]) -> Iterator[WriteToDbResult]:
        paper_id, data = record

        try:
            # Reduce down to a unique set of study type predictions for the paper
            study_types: dict[str, StudyType] = {}
            for entry in data:
                current = (
                    study_types[entry.prediction] if entry.prediction in study_types else None
                )
                if current is None or current.probability < entry.probability:
                    study_types[entry.prediction] = entry

            # There should only be a single prediction
            if len(study_types.values()) != 1:
                raise ValueError(
                    f"Failed to process: expected 1 prediction, found {len(study_types.values())}"
                )

            inference_data = InferenceData()
            study_type = inference_data.study_type.values.add()
            study_type.prediction = study_types[next(iter(study_types))].prediction
            study_type.probability = study_types[next(iter(study_types))].probability

            if not self.dry_run:
                self.paper_inferences.write(
                    paper_id=paper_id,
                    provider=PaperInference.Provider.CONSENSUS,
                    inference_data=inference_data,
                    source=self.source,
                    job_name=self.job_name,
                    timestamp=self.timestamp,
                    commit=False,
                )
                self.commit_batch_count += 1
                if self.commit_batch_count >= self.MAX_COMMIT_BATCH_COUNT:
                    self.db.commit()
                    self.commit_batch_count = 0

            yield WriteToDbResult(
                paper_id=paper_id,
                study_type=str(study_type),
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield WriteToDbResult(
                paper_id=paper_id,
                study_type=str(data),
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

    with beam.Pipeline(options=pipeline_options) as p:
        results = (
            p
            | "ReadFilesByLine" >> parquetio.ReadFromParquet(input_file_pattern)
            | "ConvertToDataclass" >> beam.Map(parquet_record_to_dataclass)
            | "GroupByPaperId" >> beam.GroupBy(lambda x: x.paper_id)
            | "WriteToDb"
            >> beam.ParDo(
                WriteToDb(
                    dry_run=dry_run,
                    db_env=db_env,
                    job_name=config.job_name,
                    timestamp=config.timestamp,
                    project_id=project_id,
                    source=input_file_pattern.removesuffix("*"),
                )
            )
        )

        write_pipeline_results(config.results_file, results)
