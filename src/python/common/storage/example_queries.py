from __future__ import annotations

import json
from typing import Optional

from common.config.constants import (
    BUCKET_NAME_WEB_DATA,
    BUCKET_NAME_WEB_DATA_DEV,
    REPO_PATH_WEB_DATA_QUERIES_JSON,
)
from common.storage.connect import StorageClient, StorageEnv
from google.cloud.storage.blob import Blob  # type: ignore
from pydantic import BaseModel

# The gcs bucket path where web data is stored.
WEB_BUCKET = f"gs://{BUCKET_NAME_WEB_DATA}"
WEB_BUCKET_DEV = f"gs://{BUCKET_NAME_WEB_DATA_DEV}"
EXAMPLE_QUERIES_JSON = "cms/example_queries.json"


def _example_queries_url(client: StorageClient) -> str:
    bucket_name = WEB_BUCKET if client.env == StorageEnv.PROD else WEB_BUCKET_DEV
    return f"{bucket_name}/{EXAMPLE_QUERIES_JSON}"


def write_example_queries_text(client: StorageClient, text: str) -> Optional[str]:
    """
    Returns the contents of the paper's clean_data_url, or None if not found.

    Raises:
        NotImplementedError: if environment not supported
    """
    if client.gcloud_client:
        example_queries_url = _example_queries_url(client)
        blob = Blob.from_string(example_queries_url, client=client.gcloud_client)
        blob.upload_from_string(text)
        return example_queries_url

    raise NotImplementedError("Write example queries not supported for environment: {client.env}.")


def read_example_queries_text(client: StorageClient) -> Optional[str]:
    """
    Returns the contents of the paper's clean_data_url, or None if not found.
    """
    if client.gcloud_client:
        example_queries_url = _example_queries_url(client)
        blob = Blob.from_string(example_queries_url, client=client.gcloud_client)
        try:
            abstract = blob.download_as_bytes().decode()
            return str(abstract)
        except Exception:
            return None
    else:
        with open(REPO_PATH_WEB_DATA_QUERIES_JSON) as f:
            return f.read()


class ExampleQueriesData(BaseModel):
    key: str
    title: str
    queries: list[str]


class HowToSearchJson(BaseModel):
    question_types: list[ExampleQueriesData]
    topics: list[ExampleQueriesData]


class ExampleQueriesJson(BaseModel):
    search_bar: list[str]
    how_to_search: HowToSearchJson
    empty_autocomplete: Optional[list[str]]


def _validate(queries_json: ExampleQueriesJson) -> None:
    if len(queries_json.search_bar) != 3:
        raise ValueError(f"Expected 3 search bar queries, found {len(queries_json.search_bar)}")


def parse_data(text: str) -> ExampleQueriesJson:
    """
    Returns validated trending queries from a file.
    """
    data = json.loads(text)
    queries = ExampleQueriesJson(**data)
    _validate(queries)
    return queries
