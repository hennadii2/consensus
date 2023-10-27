from datetime import datetime, timezone

import pytest  # type: ignore
from common.storage.datasets import extract_search_index_id


def test_extract_search_index_id_succeeds() -> None:
    timestamp = datetime.now(timezone.utc)
    path = "gs://consensus-paper-data/datasets/20220325233035/outputs/XLNET/v0.1/20220328_012637/*"
    expected = f"20220325233035-xlnet-v0_1-20220328_012637-{timestamp.strftime('%y%m%d%H%M%S')}"
    actual = extract_search_index_id(path, timestamp)
    assert actual == expected


def test_extract_search_index_id_fails_if_path_is_not_in_expected_format() -> None:
    timestamp = datetime.now(timezone.utc)
    path = "gs://consensus-paper-data/unknown-path"
    with pytest.raises(
        ValueError, match="Failed to extract search id: path not in expected format"
    ):
        extract_search_index_id(path, timestamp)
