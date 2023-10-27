import json
import os
from datetime import datetime
from typing import Tuple

from common.storage.connect import StorageClient
from loguru import logger

# TODO(cvarano): consolidate with constants.py
SEARCH_EVAL_BUCKET = "consensus-nlp-models"
SEARCH_EVAL_METRICS_PREFIX = "search/search_testing/metrics/"
SEARCH_EVAL_TO_ANNOTATE_PREFIX = "search/search_testing/to_annotate/"
SEARCH_EVAL_ANNOTATIONS_OUTPUT_PREFIX = "search/annotation_outputs/internal_annotations_editor/"
SEARCH_EVAL_CENTAUR_UPLOAD_PATH = "gs://consensus-nlp-models/search/raw_uploads/centaur_upload.csv"
SEARCH_EVAL_CENTAUR_LABELS_PATH = (
    "gs://consensus-nlp-models/search/annotation_outputs/centaur_outputs.csv"
)


def get_search_eval_metrics_base_path(suffix: str) -> Tuple[str, str]:
    """
    Generates the gcs base path and a unique run id for managing search eval metrics output.

    Args:
        suffix: A descriptive suffix to be part of the run_id. Does not need to be unique.
    Returns:
        gcs_base_path: The gcs base path for search eval metrics output
        run_id: A unique run id to keep track of all related uploads, e.g. labeling/annotations
    """
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S") + suffix
    gcs_base_path = f"gs://{os.path.join(SEARCH_EVAL_BUCKET, SEARCH_EVAL_METRICS_PREFIX, run_id)}"
    return gcs_base_path, run_id


def upload_search_eval_metrics_description(
    storage_client: StorageClient, run_id: str, description: str
):
    assert storage_client.gcloud_client is not None, "gcloud_client must be provided"
    bucket = storage_client.gcloud_client.get_bucket(SEARCH_EVAL_BUCKET)
    blob_path = os.path.join(SEARCH_EVAL_METRICS_PREFIX, run_id, "description.json")
    blob = bucket.blob(blob_path)
    blob.upload_from_string(
        data=json.dumps({"description": description}), content_type="application/json"
    )


def upload_search_eval_metrics_yaml_config(
    storage_client: StorageClient,
    config_path: str,
    run_id: str,
):
    """
    Uploads a yaml config file to gcs.

    Args:
        storage_client: StorageClient object
        run_id: A unique run id to keep track of all related uploads, e.g. labeling/annotations
        config_path: Local filepath for the config to upload
    """
    assert storage_client.gcloud_client is not None, "gcloud_client must be provided"
    bucket = storage_client.gcloud_client.get_bucket(SEARCH_EVAL_BUCKET)
    blob_path = os.path.join(SEARCH_EVAL_METRICS_PREFIX, run_id, "config.yaml")
    blob = bucket.blob(blob_path)
    blob.upload_from_filename(filename=config_path, content_type="application/yaml")
    logger.info(f"Search eval config uploaded to: gs://{SEARCH_EVAL_BUCKET}/{blob_path}")
