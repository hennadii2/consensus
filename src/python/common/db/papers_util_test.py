import pytest  # type: ignore
from common.db.papers_util import (
    encode_clean_data_hash,
    paper_provider_proto_enum_to_string,
    validate_metadata,
)
from paper_metadata_pb2 import PaperMetadata, PaperProvider


def valid_paper_metadata(provider_id: str = "providerId1") -> PaperMetadata:
    metadata = PaperMetadata()
    metadata.title = "title1"
    metadata.doi = "doi1"
    metadata.publish_year = 2022
    metadata.language = "en"
    metadata.author_names.append("author1")
    metadata.journal_name = "journal1"
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR
    metadata.provider_id = provider_id
    metadata.provider_url = "url"
    return metadata


def test_validate_metadata_fails_on_missing_required_fields() -> None:
    metadata = valid_paper_metadata()
    validate_metadata(metadata)
    assert True

    metadata = valid_paper_metadata()
    metadata.ClearField("title")
    with pytest.raises(ValueError, match="PaperMetadata is invalid: missing title"):
        validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("doi")  # Not required
    validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("publish_year")
    with pytest.raises(ValueError, match="PaperMetadata is invalid: missing publish_year"):
        validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("author_names")  # Not required
    validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("language")
    with pytest.raises(ValueError, match="PaperMetadata is invalid: missing language"):
        validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("citation_count")  # Not required
    validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("abstract_length")  # Not required
    validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("journal_name")  # Not required
    validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("provider")
    with pytest.raises(ValueError, match="PaperMetadata is invalid: missing provider"):
        validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("provider_id")
    with pytest.raises(ValueError, match="PaperMetadata is invalid: missing provider_id"):
        validate_metadata(metadata)

    metadata = valid_paper_metadata()
    metadata.ClearField("provider_url")  # Not required
    validate_metadata(metadata)


def test_paper_provider_proto_enum_to_string() -> None:
    actual = paper_provider_proto_enum_to_string(PaperProvider.SEMANTIC_SCHOLAR)
    assert actual == "SEMANTIC_SCHOLAR"


def test_encode_clean_data_hash() -> None:
    encoded = encode_clean_data_hash("test sentence to encode")
    assert encoded == "c92798c949c1adb7f245a875cf3c3269"
