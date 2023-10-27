from __future__ import annotations

import json
from typing import Optional

from common.config.constants import (
    BUCKET_NAME_WEB_DATA,
    BUCKET_NAME_WEB_DATA_DEV,
    REPO_PATH_WEB_DATA_DISPUTED_JSON,
)
from common.storage.connect import StorageClient, StorageEnv
from google.cloud.storage.blob import Blob  # type: ignore
from pydantic import BaseModel

# The gcs bucket path where web data is stored.
WEB_BUCKET = f"gs://{BUCKET_NAME_WEB_DATA}"
WEB_BUCKET_DEV = f"gs://{BUCKET_NAME_WEB_DATA_DEV}"
DISPUTED_RESULTS_JSON = "cms/disputed_results.json"


def _disputed_results_url(client: StorageClient) -> str:
    bucket_name = WEB_BUCKET if client.env == StorageEnv.PROD else WEB_BUCKET_DEV
    return f"{bucket_name}/{DISPUTED_RESULTS_JSON}"


def write_disputed_results_text(client: StorageClient, text: str) -> Optional[str]:
    """
    Overwrites the current contents of disputed results with given text.

    Raises:
        NotImplementedError: if environment not supported
    """
    if client.gcloud_client:
        disputed_results_url = _disputed_results_url(client)
        blob = Blob.from_string(disputed_results_url, client=client.gcloud_client)
        blob.upload_from_string(text)
        return disputed_results_url

    raise NotImplementedError(
        "Write disputed results not supported for environment: {client.env}."
    )


def read_disputed_results_text(client: StorageClient) -> Optional[str]:
    """
    Returns the contents of disputed results, or None if not found.
    """
    if client.gcloud_client is not None:
        disputed_results_url = _disputed_results_url(client)
        blob = Blob.from_string(disputed_results_url, client=client.gcloud_client)
        try:
            abstract = blob.download_as_bytes().decode()
            return str(abstract)
        except Exception:
            return None
    else:
        with open(REPO_PATH_WEB_DATA_DISPUTED_JSON) as f:
            return f.read()


class DisputedPaperJson(BaseModel):
    key: str
    reason: str
    url: str
    paper_ids: list[str]


class DisputedResultsJson(BaseModel):
    disputed_papers: list[DisputedPaperJson]
    known_background_claim_ids: list[str]


def _validate(disputed_json: DisputedResultsJson) -> None:
    if len(disputed_json.disputed_papers) <= 0:
        raise ValueError(
            f"Expected > 1 disputed paper, found {len(disputed_json.disputed_papers)}"
        )


def parse_data(disputed_results_json: Optional[str]) -> Optional[DisputedResultsJson]:
    """
    Returns the contents of disputed results parsed into a model.
    """
    if disputed_results_json is None:
        return None

    data = json.loads(disputed_results_json)
    queries = DisputedResultsJson(**data)
    _validate(queries)
    return queries
