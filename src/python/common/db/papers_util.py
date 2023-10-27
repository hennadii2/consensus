from __future__ import annotations

from hashlib import md5
from typing import Optional

from paper_metadata_pb2 import PaperMetadata, PaperProvider


def validate_metadata(metadata: Optional[PaperMetadata]) -> None:
    """Raises an error if metadata is missing required fields."""
    if not metadata:
        raise ValueError("PaperMetadata is invalid: missing metadata")

    if not metadata.title:
        raise ValueError("PaperMetadata is invalid: missing title")

    if not metadata.publish_year:
        raise ValueError("PaperMetadata is invalid: missing publish_year")

    if not metadata.language:
        raise ValueError("PaperMetadata is invalid: missing language")

    if not metadata.provider:
        raise ValueError("PaperMetadata is invalid: missing provider")

    if not metadata.provider_id:
        raise ValueError("PaperMetadata is invalid: missing provider_id")


def paper_provider_proto_enum_to_string(provider: PaperProvider.V) -> str:
    """Returns a string representation of the PaperProvider proto enum."""
    return str(PaperProvider.DESCRIPTOR.values_by_number[provider].name)


def encode_clean_data_hash(abstract: str) -> str:
    """Returns hex representation of given abstract text."""
    md5_hash = md5(abstract.encode())
    return md5_hash.hexdigest()
