from dataclasses import dataclass
from datetime import datetime, timezone

from common.config.constants import BUCKET_NAME_PIPELINE_LOGS

# The maximum number of workers to allocate to Dataflow jobs
MAX_NUM_WORKERS = 70


@dataclass(frozen=True)
class PipelineConfig:
    job_name: str
    temp_dir: str
    results_file: str
    timestamp: datetime
    max_num_workers: int


def get_pipeline_config(pipeline: str) -> PipelineConfig:
    """
    Returns standardized configuration options to be used in pipeline runners.
    """
    output_dir = f"gs://{BUCKET_NAME_PIPELINE_LOGS}"

    timestamp = datetime.now(timezone.utc)
    job_name = f"{pipeline}-{timestamp.strftime('%y%m%d%H%M%S')}"
    temp_dir = f"{output_dir}/temp/{pipeline}"
    results_file = f"{output_dir}/results/{pipeline}/{job_name}/{job_name}"
    return PipelineConfig(
        job_name=job_name,
        temp_dir=temp_dir,
        results_file=results_file,
        timestamp=timestamp,
        max_num_workers=MAX_NUM_WORKERS,
    )
