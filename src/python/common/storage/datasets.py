from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Tuple

from common.config.constants import BUCKET_NAME_PAPER_DATA
from common.storage.connect import StorageEnv

# The gcs bucket path where parsed paper data and model output is stored.
DATASETS_BUCKET = f"gs://{BUCKET_NAME_PAPER_DATA}/datasets"


def get_new_dataset_id_and_path(env: StorageEnv) -> Tuple[str, str]:
    """
    Return a new [dataset id, storage path] for a dataset based on the current timestamp.

    A dataset is a set of cleaned paper abstracts tokenized into sentences and
    saved to parquet files to be used by ML models.

    Raises:
        NotImplementedError: if environment not supported
    """
    if env == StorageEnv.DEV or env == StorageEnv.PROD:
        timestamp = datetime.now(timezone.utc)
        dataset_id = timestamp.strftime("%Y%m%d%H%M%S")
        dataset_url = f"{DATASETS_BUCKET}/{dataset_id}/parsed/sentences.parquet"
        return dataset_id, dataset_url

    raise NotImplementedError("Get new dataset path not supported for environment: {env}.")


def extract_search_index_id(path: str, timestamp: datetime) -> str:
    """
    Returns a parsed search index ID from a model output path, where the ID is
    formatted for use as an elasticsearch index name.

    Raises:
        ValueError: if results path is not in the expected format
    """
    parsed = re.search(f"{DATASETS_BUCKET}/(.*)/outputs/(.*)/(.*)/(.*)/.*$", path)
    if not parsed:
        raise ValueError("Failed to extract search id: path not in expected format")

    translation = str.maketrans({".": "_", "/": "_"})
    dataset_id = parsed.group(1).translate(translation)
    model_type = parsed.group(2).translate(translation)
    model_id = parsed.group(3).translate(translation)
    run_id = parsed.group(4).translate(translation)

    run_timestamp = timestamp.strftime("%y%m%d%H%M%S")

    search_index_id = "-".join([dataset_id, model_type, model_id, run_id, run_timestamp])
    return search_index_id.lower()


def search_index_id_without_run_timestamp(search_index_id: str) -> str:
    """
    Removes run timestamp to create a common ID for all search indexes populated
    from the same dataset.
    """
    return "-".join(search_index_id.split("-")[:-1])
