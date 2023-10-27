import pytest  # type: ignore
from common.beam.records.base_record import extract_version_from_input_file


def test_extract_record_from_input_file_succeeds() -> None:
    actual = extract_version_from_input_file(
        input_file="gs://consensus-paper-data/features/papers/230524074450_new_and_existing_needs_reprocessing/outputs.parquet",  # noqa: E501
        expected_gcs_prefix="gs://consensus-paper-data/features/papers/",
    )
    assert actual == "230524074450_new_and_existing_needs_reprocessing"


def test_extract_record_from_input_file_fails() -> None:
    with pytest.raises(ValueError):
        # Test wrong expected prefix
        extract_version_from_input_file(
            input_file="gs://consensus-paper-data/features/papers/230524074450_new_and_existing_needs_reprocessing/outputs.parquet",  # noqa: E501
            expected_gcs_prefix="gs://consensus-paper-data/features/claims/",
        )

    with pytest.raises(ValueError):
        # Test missing datetime prefix
        extract_version_from_input_file(
            input_file="gs://consensus-paper-data/features/papers/new_and_existing_needs_reprocessing/outputs.parquet",  # noqa: E501
            expected_gcs_prefix="gs://consensus-paper-data/features/papers/",
        )
