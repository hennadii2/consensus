import os
from dataclasses import dataclass
from typing import Any, Iterator, Optional

import apache_beam as beam  # type: ignore
from apache_beam.options.pipeline_options import PipelineOptions, SetupOptions  # type: ignore
from common.beam.pipeline_config import PipelineConfig
from common.beam.pipeline_result import PipelineResult, write_pipeline_results
from common.config.secret_manager import SecretId, access_secret
from common.ingestion.download import (
    download_s2_dataset_file,
    get_all_s2_download_paths_for_latest_release,
)
from common.ingestion.semantic_scholar.api import DatasetDownloadPath
from common.storage.connect import StorageEnv, init_storage_client


@dataclass(frozen=True)
class DownloadDatasetFileResult(PipelineResult):
    download_path: str
    upload_path: Optional[str]
    dry_run: bool


class DownloadDatasetFile(beam.DoFn):
    """
    Beam DoFn to download a dataset file to GCS.
    """

    def __init__(
        self,
        dry_run: bool,
        project_id: str,
        storage_env: StorageEnv,
    ):
        self.dry_run = dry_run
        self.project_id = project_id
        self.storage_env = storage_env

    def setup(self):
        # Add project ID to worker environment to allow connection to
        # secret manager
        os.environ[SecretId.GCLOUD_PROJECT_ID.name] = self.project_id

        self.storage_client = init_storage_client(self.storage_env)

    def process(self, record: DatasetDownloadPath) -> Iterator[DownloadDatasetFileResult]:
        try:
            if not self.storage_client.gcloud_client:
                raise ValueError("Gcloud storage client not initialized")

            gcs_upload_url = download_s2_dataset_file(
                client=self.storage_client.gcloud_client,
                download_path=record,
                dry_run=self.dry_run,
            )
            yield DownloadDatasetFileResult(
                download_path=record.download_path,
                upload_path=gcs_upload_url,
                dry_run=self.dry_run,
                success=True,
                message=None,
            )
        except Exception as e:
            yield DownloadDatasetFileResult(
                download_path=record.download_path,
                upload_path=None,
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

    s2_token = access_secret(SecretId.S2_API_KEY)
    all_dataset_download_paths = get_all_s2_download_paths_for_latest_release(s2_token)

    with beam.Pipeline(options=pipeline_options) as p:
        results = (
            p
            | "CreateDatasetDownloadPaths" >> beam.Create(all_dataset_download_paths)
            | "DownloadDatasetFiles"
            >> beam.ParDo(DownloadDatasetFile(dry_run, project_id, storage_env))
        )

        write_pipeline_results(config.results_file, results)
