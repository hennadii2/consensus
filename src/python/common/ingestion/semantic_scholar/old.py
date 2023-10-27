from typing import Any, List, Optional

from common.ingestion.util import detect_language
from paper_metadata_pb2 import PaperMetadata, PaperProvider
from pydantic import BaseModel


class SemanticScholarAuthorJson(BaseModel):
    name: str
    # S2 generated ID
    ids: List[str]


class SemanticScholarJson(BaseModel):
    """
    Schema for raw Semantic Scholar (S2) records.
    See documentation here: https://api.semanticscholar.org/corpus
    """

    id: str
    title: Optional[str]
    paperAbstract: Optional[str]
    entities: Optional[List[Any]]
    s2Url: Optional[str]
    pdfUrls: List[Optional[str]]
    # Deprecated 2020-05-27
    s2PdfUrl: Optional[str]
    authors: Optional[List[SemanticScholarAuthorJson]]
    # Number of S2 papers which cited this paper
    inCitations: Optional[List[str]]
    # Number of S2 papers which this paper cited
    outCitations: Optional[List[str]]
    fieldsOfStudy: Optional[List[str]]
    year: Optional[int]
    venue: Optional[str]
    journalName: Optional[str]
    journalVolume: Optional[str]
    journalPages: Optional[str]
    sources: Optional[List[str]]
    doi: Optional[str]
    doiUrl: Optional[str]
    # Unique identifier used by PubMed
    pmid: Optional[str]
    # Unique identifier used by Microsoft Academic Graph
    magId: Optional[str]


def semantic_scholar_to_metadata(semantic: SemanticScholarJson) -> PaperMetadata:
    """Converts a raw Semantic Scholar record to the PaperMetadata format"""

    metadata = PaperMetadata()
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR

    if semantic.title:
        metadata.title = semantic.title

    if semantic.doi:
        metadata.doi = semantic.doi

    if semantic.year:
        metadata.publish_year = semantic.year

    language = detect_language(
        title=semantic.title,
        abstract=semantic.paperAbstract,
    )
    if language:
        metadata.language = language

    if semantic.authors:
        for author in semantic.authors:
            metadata.author_names.append(author.name)

    if semantic.inCitations:
        metadata.citation_count = len(semantic.inCitations)

    if semantic.paperAbstract:
        metadata.abstract_length = len(semantic.paperAbstract)

    if semantic.journalName:
        metadata.journal_name = semantic.journalName

    if semantic.id:
        metadata.provider_id = semantic.id

    if semantic.s2Url:
        metadata.provider_url = semantic.s2Url

    return metadata
