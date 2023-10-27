from enum import Enum
from typing import Optional

from pydantic import BaseModel
from web.backend.app.common.badges import Badges

LOG_ENDPOINT = "search"


class LOG_EVENTS(Enum):
    LOAD_CACHE = "load_from_cache"
    READ_DB = "read_all_claims_from_db"
    RUN_SEARCH_FULL = "run_search_full"
    ENCODE_EMBEDDING = "encode_embedding"
    CLEAN_TEXT = "clean_text"
    QUERY_EXPANSION = "query_expansion"
    RUN_SEARCH = "run_search"
    EXTRACT_ANSWERS = "extract_answers"
    QA_RERANK = "qa_rerank"
    YES_NO_CLASSIFIER = "yes_no_question_classifier"
    QUERY_CLASSIFIER = "query_classifier"
    OFFENSIVE_QUERY_CLASSIFIER = "offensive_query_classifier"


class ClaimModel(BaseModel):
    # The ID of a single claim result.
    id: str
    paper_id: str
    # The text of the claim.
    text: str
    journal: str
    title: str
    primary_author: str
    authors: list[str]
    year: int
    url_slug: str
    doi: str
    volume: str
    pages: str
    badges: Badges


class SearchResponse(BaseModel):
    # Unique ID for this search, used to look up cache keys in other endpoints
    id: str
    # Ordered results returned for the search
    claims: list[ClaimModel]
    # True if there are no more results available for a next page
    isEnd: bool
    # True if query is as a yes/no question, None if classifier was not run
    isYesNoQuestion: Optional[bool]
    # True if query is as a question, None if classifier was not run
    canSynthesize: Optional[bool]
    # True if we allow synthesis on the query, None if classifier was not run
    nuanceRequired: Optional[bool]
    # True if some form of synthesis will succeed, None if logic was not run
    canSynthesizeSucceed: Optional[bool]
    # Number of total top results, above or below relevancy threshold
    numTopResults: Optional[int]
    # Number of results above the relevancy threshold
    numRelevantResults: Optional[int]
