import re

from common.storage.gcs_util import get_search_eval_metrics_base_path

TIMESTAMP_PATTERN = re.compile(r"\d{8}_\d{6}")


def test_get_search_eval_metrics_base_path():
    actual_base_path, actual_run_id = get_search_eval_metrics_base_path(suffix="_test")
    # extract generated timestamp for comparison
    timestamp_match = re.match(TIMESTAMP_PATTERN, actual_run_id)
    assert timestamp_match is not None

    expected_run_id = timestamp_match.group() + "_test"
    assert actual_run_id == expected_run_id
    expected_base_path = (
        f"gs://consensus-nlp-models/search/search_testing/metrics/{expected_run_id}"
    )
    assert actual_base_path == expected_base_path
