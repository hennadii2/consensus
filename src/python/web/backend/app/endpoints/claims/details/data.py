from enum import Enum
from typing import Optional

from pydantic import BaseModel
from web.backend.app.endpoints.papers.details.data import PaperDetails

CLAIM_DETAILS_LOG_ENDPOINT = "claim_details"


class LOG_EVENTS(Enum):
    LOAD_FROM_CACHE = "load_from_cache"
    READ_BADGES = "read_badges"
    READ_CLAIM = "read_claim_from_index"
    READ_DB = "read_paper_from_db"
    READ_SJR_QUARTILE = "read_sjr_quartile"
    READ_STORAGE = "read_abstract_from_storage"


class ClaimDetails(BaseModel):
    # ID of the claim in search index
    id: str
    # Text of the claim
    text: str
    url_slug: str


class ClaimDetailsResponse(BaseModel):
    """
    A response from the /claims/details endpoint.
    """

    # Details on the claim.
    claim: Optional[ClaimDetails]
    # Details on the paper for the claim.
    paper: Optional[PaperDetails]
    # If V2 is enabled, this will be set with the claim's paper ID
    paperIdForRedirect: Optional[str]


EMPTY_RESPONSE = ClaimDetailsResponse(
    claim=None,
    paper=None,
)
