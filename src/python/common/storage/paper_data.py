from __future__ import annotations

from datetime import datetime
from typing import Optional

from common.config.constants import BUCKET_NAME_PAPER_DATA, BUCKET_NAME_PAPER_DATA_DEV
from common.storage.connect import StorageClient, StorageEnv
from google.cloud.storage.blob import Blob  # type: ignore
from paper_metadata_pb2 import PaperProvider
from paper_pb2 import Paper

# The gcs bucket path where cleaned paper abstracts are stored.
CLEANED_BUCKET = f"gs://{BUCKET_NAME_PAPER_DATA}/cleaned"
CLEANED_BUCKET_DEV = f"gs://{BUCKET_NAME_PAPER_DATA_DEV}/cleaned"

# The gcs bucket path where raw datasets are stored.
RAW_DATA_BUCKET = f"gs://{BUCKET_NAME_PAPER_DATA}/raw"


def get_raw_data_path(
    provider: PaperProvider.V, release_id: str, dataset: str, filename: str
) -> str:
    if provider == PaperProvider.SEMANTIC_SCHOLAR:
        return f"{RAW_DATA_BUCKET}/s2/{release_id}/{dataset}/{filename}"
    else:
        raise NotImplementedError("Raw data path not supported for paper source: {provider}")


def _write_clean_abstract(
    client: StorageClient,
    clean_abstract: str,
    paper_id: str,
    base_dir: str,
    timestamp: datetime,
) -> str:
    """
    Writes a paper abstract to the appropriate location in blob store and returns the URL.

    Raises:
        NotImplementedError: if environment not supported
    """
    version = timestamp.strftime("%Y%m%d%H%M%S")
    abstract_path = f"{base_dir}/{paper_id}/{version}/abstract.txt"

    if client.gcloud_client:
        bucket_name = CLEANED_BUCKET if client.env == StorageEnv.PROD else CLEANED_BUCKET_DEV
        clean_data_url = f"{bucket_name}/{abstract_path}"
        blob = Blob.from_string(clean_data_url, client=client.gcloud_client)
        blob.upload_from_string(clean_abstract)
        return clean_data_url

    raise NotImplementedError("Write clean abstract not supported for environment: {client.env}.")


def write_clean_abstract_to_v2_storage(
    client: StorageClient,
    clean_abstract: str,
    paper_id: str,
    timestamp: datetime,
) -> str:
    """
    Writes a paper abstract to the appropriate location in blob store and returns the URL.

    Raises:
        NotImplementedError: if environment not supported
    """
    return _write_clean_abstract(
        client=client,
        clean_abstract=clean_abstract,
        paper_id=paper_id,
        base_dir="by_v2_paper_id",
        timestamp=timestamp,
    )


def write_clean_abstract(
    client: StorageClient,
    clean_abstract: str,
    paper: Paper,
    timestamp: datetime,
) -> str:
    """
    Writes a paper abstract to the appropriate location in blob store and returns the URL.

    Raises:
        NotImplementedError: if environment not supported
    """
    return _write_clean_abstract(
        client=client,
        clean_abstract=clean_abstract,
        paper_id=str(paper.id),
        base_dir="by_paper_id",
        timestamp=timestamp,
    )


def read_clean_abstract(
    client: StorageClient,
    paper: Paper,
) -> Optional[str]:
    """
    Returns the contents of the paper's clean_data_url, or None if not found.

    Raises:
        NotImplementedError: if environment not supported
    """

    if client.gcloud_client:
        blob = Blob.from_string(paper.clean_data_url, client=client.gcloud_client)
        try:
            abstract = blob.download_as_bytes().decode()
            return str(abstract)
        except Exception:
            return None
    else:
        with open(paper.clean_data_url) as f:
            return f.read()
