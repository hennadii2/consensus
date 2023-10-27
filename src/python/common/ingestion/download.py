import os
import tempfile

import google.cloud.storage as storage  # type: ignore
import requests
from common.ingestion.semantic_scholar.api import (
    DatasetDownloadPath,
    get_dataset_download_paths,
    get_latest_release_summary,
)
from common.storage.paper_data import get_raw_data_path
from google.cloud.storage.blob import Blob  # type: ignore
from paper_metadata_pb2 import PaperProvider


def get_all_s2_download_paths_for_latest_release(s2_token: str) -> list[DatasetDownloadPath]:
    """
    Helper to return all dataset downloads paths for the latest semantic scholar release.
    """
    latest_release = get_latest_release_summary(s2_token)
    all_dataset_download_paths = []
    for dataset in latest_release.datasets:
        download_paths = get_dataset_download_paths(
            token=s2_token,
            release=latest_release,
            dataset=dataset,
        )
        all_dataset_download_paths += download_paths
    return all_dataset_download_paths


def download_s2_dataset_file(
    client: storage.Client, download_path: DatasetDownloadPath, dry_run: bool
) -> str:
    """
    Downloads a semantic scholar dataset file to GCS and returns the GCS path.

    Raises:
        ValueError: if dataset file already exists in GCS
    """
    gcs_upload_url = get_raw_data_path(
        provider=PaperProvider.SEMANTIC_SCHOLAR,
        release_id=download_path.release_id,
        dataset=download_path.dataset,
        filename=download_path.filename,
    )
    blob = Blob.from_string(
        gcs_upload_url,
        client=client,
    )
    if blob.exists():
        raise ValueError("Failed to upload: dataset file already exists")

    if not dry_run:
        tmp_file = os.path.join(tempfile.gettempdir(), download_path.filename)
        with open(tmp_file, "wb") as file_obj:
            data = requests.get(download_path.download_path)
            file_obj.write(data.content)
        blob.upload_from_filename(tmp_file)
        # cleanup
        os.remove(tmp_file)

    return gcs_upload_url
