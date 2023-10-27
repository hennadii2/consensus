from __future__ import annotations

import json
from typing import Optional, Tuple

from common.ingestion.semantic_scholar.data_mappings import (
    S2Metadata,
    s2_metadata_to_paper_metadata,
)
from common.ingestion.semantic_scholar.old import SemanticScholarJson, semantic_scholar_to_metadata
from paper_metadata_pb2 import PaperMetadata, PaperProvider

MIN_ABSTRACT_LENGTH = 250  # characters


def filter_metadata_for_product(metadata: PaperMetadata) -> None:
    """
    Raises an error if metadata should not be ingested into our product.

    Raises:
        ValueError: if a required condition is not met
    """
    if metadata.language != "en":
        raise ValueError("Filtered for product: language is not english")
    if not metadata.journal_name and not metadata.doi:
        raise ValueError("Filtered for product: missing journal name and doi")
    if not metadata.abstract_length:
        raise ValueError("Filtered for product: missing required field abstract_length")
    if metadata.abstract_length < MIN_ABSTRACT_LENGTH:
        raise ValueError(f"Filtered for product: abstract_length is < {MIN_ABSTRACT_LENGTH}")


def filter_metadata_for_ingestion(metadata: PaperMetadata) -> None:
    """
    Raises an error if metadata should not be ingested into our database.

    Raises:
        ValueError: if a required condition is not met
    """
    if not metadata.provider:
        raise ValueError("Filtered for ingestion: missing required field provider")
    if not metadata.provider_id:
        raise ValueError("Filtered for ingestion: missing required field provider_id")
    if not metadata.provider_url:
        raise ValueError("Filtered for ingestion: missing required field provider_url")
    if not metadata.title:
        raise ValueError("Filtered for ingestion: missing required field title")
    if not metadata.publish_year:
        raise ValueError("Filtered for ingestion: missing required field publish_year")


def extract_metadata_and_abstract(
    provider: PaperProvider.V,
    text: str,
    try_old_formats: bool = True,
) -> Tuple[PaperMetadata, Optional[str]]:
    """
    Converts a raw paper record from an external provider into a tuple of
    its PaperMetadata and raw abstract text.

    Raises:
        NotImplementedError: if conversion for a provider is not yet supported
    """

    if provider == PaperProvider.SEMANTIC_SCHOLAR:
        try:
            # First try to load with latest data format
            data = json.loads(text)
            s2_metadata = S2Metadata(**data)
            metadata = s2_metadata_to_paper_metadata(s2_metadata)
            abstract = (
                None if s2_metadata.added_abstract is None else s2_metadata.added_abstract.abstract
            )
            return (metadata, abstract)
        except Exception as e:
            if not try_old_formats:
                raise e
            # Otherwise fall back to old format
            data = json.loads(text)
            semantic_scholar_json = SemanticScholarJson(**data)
            metadata = semantic_scholar_to_metadata(semantic_scholar_json)
            return (metadata, str(semantic_scholar_json.paperAbstract))
    else:
        raise NotImplementedError(
            "Metadata and abstract extraction not supported for paper source: {provider}"
        )


def extract_metadata(
    provider: PaperProvider.V,
    text: str,
    try_old_formats: bool = True,
) -> PaperMetadata:
    """
    Converts a raw paper record from an external provider into PaperMetadata,
    which is our internal format with common mappings across providers.

    Raises:
        NotImplementedError: if conversion for a provider is not yet supported
    """

    if provider == PaperProvider.SEMANTIC_SCHOLAR:
        try:
            # First try to load with latest data format
            data = json.loads(text)
            s2_metadata = S2Metadata(**data)
            return s2_metadata_to_paper_metadata(s2_metadata)
        except Exception as e:
            if not try_old_formats:
                raise e
            # Otherwise fall back to old format
            data = json.loads(text)
            semantic_scholar_json = SemanticScholarJson(**data)
            return semantic_scholar_to_metadata(semantic_scholar_json)
    else:
        raise NotImplementedError("Metadata extraction not supported for paper source: {provider}")
