import hashlib
import os
from datetime import datetime
from enum import Enum
from typing import Optional

import pyarrow  # type: ignore
from pydantic import BaseModel


class RecordStatus(Enum):
    """
    Represents the processing state of the feature record.
    """

    ACTIVE = "active"
    ERROR = "error"
    DELETED = "deleted"


class RecordDataHash(BaseModel):
    """
    Bundled model for different data hash versions.
    """

    input_data_hash: Optional[str]
    method_version_hash: Optional[str]
    output_data_hash: str


class BaseFeatureRecord(BaseModel):
    """
    Base dataclass for extracted feature records.
    """

    class Config:
        arbitrary_types_allowed = True

    status: RecordStatus
    # Typically only set if status == ERROR
    status_msg: Optional[str]
    # A string representing the input data
    input_data_hash: Optional[str]
    # A string representing the method used to created the output data
    # This does not have to be a true hash, but can be any string description.
    # For example: model names and versions used to produce the data
    method_version_hash: str
    # Timestamp of generation of this record in UTC ISO format
    timestamp_iso: str


BaseFeatureRecordParquetSchemaFields = [
    ("status", pyarrow.string()),
    ("status_msg", pyarrow.string()),
    ("input_data_hash", pyarrow.string()),
    ("method_version_hash", pyarrow.string()),
    ("timestamp_iso", pyarrow.string()),
]


def hash_data_string(data: str) -> str:
    """
    Converts a string into a consistent and shortened hash representation.
    """
    return hashlib.sha256(data.encode()).hexdigest()[:8]


def extract_version_from_input_file(input_file: str, expected_gcs_prefix: str) -> str:
    """
    Returns a version parsed from an input file.

    Raises:
        ValueError: if expected version can't be parsed from input file
    """
    if not input_file.startswith(expected_gcs_prefix):
        raise ValueError(
            "Failed to extract_version_from_input_file: "
            + "input file does not start with expected prefix. "
            + f"expected: {expected_gcs_prefix} actual: {input_file}",
        )
    version = os.path.dirname(input_file.removeprefix(expected_gcs_prefix))

    datetime_prefix = version.split("_")[0]
    try:
        datetime.strptime(datetime_prefix, "%y%m%d%H%M%S")
    except Exception:
        raise ValueError(
            "Failed to extract_version_from_input_file: "
            + f"version does not start with datetime prefix: {datetime_prefix}"
        )
    return version
