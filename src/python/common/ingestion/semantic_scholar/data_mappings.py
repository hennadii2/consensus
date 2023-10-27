import re
from datetime import datetime, timezone
from typing import Optional

from common.ingestion.util import detect_language
from common.time.convert import TimeUnit, datetime_to_unix
from paper_metadata_pb2 import DerivedData, PaperMetadata, PaperProvider
from pydantic import BaseModel

PUBLICATION_DATE_REGEX = re.compile("[0-9]{4}-[0-9]{2}-[0-9]{2}")


class S2OpenAccessInfo(BaseModel):
    externalids: dict[str, Optional[str]]
    license: Optional[str]
    url: Optional[str]
    status: Optional[str]


class S2Abstract(BaseModel):
    """
    Schema for raw Semantic Scholar (S2) abstract dataset records.
    """

    corpusid: str
    openaccessinfo: S2OpenAccessInfo
    abstract: str
    updated: str


class S2AuthorJson(BaseModel):
    authorId: Optional[str]
    name: str


class S2FieldsOfStudy(BaseModel):
    category: str
    source: str


class S2Journal(BaseModel):
    name: Optional[str]
    volume: Optional[str]
    pages: Optional[str]


class S2MetadataExernalIds(BaseModel):
    ACL: Optional[str]
    DBLP: Optional[str]
    ArXiv: Optional[str]
    MAG: Optional[str]
    CorpusId: str
    PubMed: Optional[str]
    DOI: Optional[str]
    PubMedCentral: Optional[str]


class S2Metadata(BaseModel):
    """
    Schema for raw Semantic Scholar (S2) papers dataset records.
    """

    corpusid: str
    externalids: S2MetadataExernalIds
    url: Optional[str]
    title: Optional[str]
    authors: Optional[list[S2AuthorJson]]
    venue: Optional[str]
    year: Optional[int]
    referencecount: int
    citationcount: int
    influentialcitationcount: int
    isopenaccess: bool
    s2fieldsofstudy: Optional[list[S2FieldsOfStudy]]
    publicationtypes: Optional[list[str]]
    publicationdate: Optional[str]
    journal: Optional[S2Journal]
    updated: Optional[str]
    added_abstract: Optional[S2Abstract]


def parse_s2_datetime(time: Optional[str]) -> datetime:
    if time is not None:
        try:
            return datetime.strptime(time.removesuffix("Z") + "+0000", "%Y-%m-%dT%H:%M:%S.%f%z")
        except Exception:
            pass

        try:
            return datetime.strptime(time.removesuffix("Z") + "+0000", "%Y-%m-%dT%H:%M:%S%z")
        except Exception:
            pass

    return datetime.now(timezone.utc)


def s2_metadata_to_paper_metadata(s2: S2Metadata) -> PaperMetadata:
    """Converts a raw Semantic Scholar record to the PaperMetadata format"""

    metadata = PaperMetadata()
    metadata.provider = PaperProvider.SEMANTIC_SCHOLAR
    abstract = s2.added_abstract.abstract if s2.added_abstract else None
    updated_usec = datetime_to_unix(parse_s2_datetime(s2.updated), TimeUnit.MICROSECONDS)

    if s2.title is not None:
        metadata.title = s2.title

    if s2.externalids.DOI is not None:
        metadata.doi = s2.externalids.DOI

    if s2.year is not None:
        metadata.publish_year = s2.year

    if s2.publicationdate is not None:
        if PUBLICATION_DATE_REGEX.match(s2.publicationdate) is not None:
            metadata.publish_date = s2.publicationdate
            if not metadata.publish_year:
                metadata.publish_year = int(s2.publicationdate[0:4])

    language = detect_language(
        title=s2.title,
        abstract=abstract,
    )
    if language is not None:
        metadata.language = language

    if s2.authors is not None:
        for author in s2.authors:
            if author.name is not None:
                metadata.author_names.append(author.name)

    if s2.citationcount is not None:
        metadata.citation_count = s2.citationcount

    if abstract is not None:
        metadata.abstract_length = len(abstract)

    if s2.journal is not None and s2.journal.name is not None:
        metadata.journal_name = s2.journal.name

    if s2.corpusid is not None:
        metadata.provider_id = s2.corpusid

    if s2.url is not None:
        metadata.provider_url = s2.url

    if s2.s2fieldsofstudy is not None:
        for field_of_study in s2.s2fieldsofstudy:
            derived_data = DerivedData()
            derived_data.provider = DerivedData.Provider.SEMANTIC_SCHOLAR
            derived_data.description = field_of_study.source
            derived_data.created_at_usec = updated_usec
            derived_data.string_data = field_of_study.category
            metadata.fields_of_study.append(derived_data)

    return metadata
