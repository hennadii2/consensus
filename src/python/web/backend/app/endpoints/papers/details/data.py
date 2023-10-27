from enum import Enum
from typing import Optional

from pydantic import BaseModel
from web.backend.app.common.badges import Badges

PAPER_DETAILS_LOG_ENDPOINT = "paper_details"
PAPER_DETAILS_LIST_LOG_ENDPOINT = "paper_details_list"


class LOG_EVENTS(Enum):
    LOAD_FROM_CACHE = "load_from_cache"
    READ_ABSTRACT_TAKEAWAY = "read_abstract_takeaway"
    READ_BADGES = "read_badges"
    READ_DB = "read_paper_from_db"
    READ_PAPER = "read_paper_from_index"
    READ_SJR_QUARTILE = "read_sjr_quartile"
    READ_STORAGE = "read_abstract_from_storage"


class JournalDetails(BaseModel):
    # Name of the journal
    title: str
    scimago_quartile: Optional[int] = None


class PaperDetails(BaseModel):
    abstract: Optional[str]
    abstract_takeaway: str
    authors: list[str]
    badges: Optional[Badges]
    # Number of incoming citations to the paper
    citation_count: int
    doi: str
    id: str
    journal: JournalDetails
    pages: str
    provider_url: str
    title: str
    url_slug: Optional[str]
    volume: str
    year: int


class PaperDetailsResponse(PaperDetails):
    pass


class PaperDetailsListResponse(BaseModel):
    """
    A response from the /papers/details?paper_ids=1,2,3 endpoint
    """

    paperDetailsListByPaperId: dict[str, PaperDetails]
