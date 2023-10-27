from __future__ import annotations

import json
from pathlib import Path

import pytest  # type: ignore
from common.db.papers_util import validate_metadata
from common.ingestion.extract import (
    extract_metadata,
    filter_metadata_for_ingestion,
    filter_metadata_for_product,
)
from google.protobuf.json_format import ParseDict
from paper_metadata_pb2 import PaperMetadata, PaperProvider

TEST_DATA_PATH = "src/python/common/ingestion/test_data"


def test_extract_metadata_for_semantic_scholar_succeeds() -> None:
    semantic_test_data = [
        (
            f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_1_raw",
            f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_1_extracted",
        ),
        (
            f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_2_raw",
            f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_2_extracted",
        ),
        (
            f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_3_raw",
            f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_3_extracted",
        ),
    ]
    for test_data in semantic_test_data:
        raw_path, expected_path = test_data
        actual = extract_metadata(
            PaperProvider.SEMANTIC_SCHOLAR,
            Path(raw_path).read_text(),
        )
        expected = ParseDict(
            json.loads(Path(expected_path).read_text()),
            PaperMetadata(),
        )
        validate_metadata(actual)  # test that metadata is in required format
        assert actual == expected


def test_filter_metadata_for_ingestion_raises_error_if_missing_required_fields() -> None:
    example = Path(f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_2_raw").read_text()

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    filter_metadata_for_ingestion(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.ClearField("provider_id")
    with pytest.raises(
        Exception, match="Filtered for ingestion: missing required field provider_id"
    ):
        filter_metadata_for_ingestion(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.ClearField("title")
    with pytest.raises(Exception, match="Filtered for ingestion: missing required field title"):
        filter_metadata_for_ingestion(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.ClearField("publish_year")
    with pytest.raises(
        Exception, match="Filtered for ingestion: missing required field publish_year"
    ):
        filter_metadata_for_ingestion(metadata)


def test_filter_metadata_for_product_raises_error_if_missing_required_fields() -> None:
    example = Path(f"{TEST_DATA_PATH}/semantic_scholar_2022-01-01_000_2_raw").read_text()

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    filter_metadata_for_product(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.language = "fr"
    with pytest.raises(Exception, match="Filtered for product: language is not english"):
        filter_metadata_for_product(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.ClearField("doi")
    metadata.ClearField("journal_name")
    with pytest.raises(Exception, match="Filtered for product: missing journal name and doi"):
        filter_metadata_for_product(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.ClearField("abstract_length")
    with pytest.raises(
        Exception, match="Filtered for product: missing required field abstract_length"
    ):
        filter_metadata_for_product(metadata)

    metadata = extract_metadata(PaperProvider.SEMANTIC_SCHOLAR, example)
    metadata.abstract_length = 100
    with pytest.raises(Exception, match="Filtered for product: abstract_length is < 250"):
        filter_metadata_for_product(metadata)
