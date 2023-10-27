from enum import Enum
from typing import Optional

from pydantic import BaseModel
from web.backend.app.common.badges import Badges

LOG_ENDPOINT = "paper_search"


class LOG_EVENTS(Enum):
    LOAD_CACHE = "load_from_cache"
    READ_DB = "read_all_claims_from_db"
    RUN_SEARCH_FULL = "run_search_full"
    ENCODE_EMBEDDING = "encode_embedding"
    CLEAN_TEXT = "clean_text"
    RUN_SEARCH = "run_search"
    EXTRACT_ANSWERS = "extract_answers"
    EXTRACT_ANSWERS_AND_RERANK = "extract_answers_and_rerank"
    QA_RERANK = "qa_rerank"
    ANALYZE_QUERY = "analyze_query"
    LOOKUP_ABSTRACT_TAKEAWAYS = "lookup_abstract_takeaways"


class PaperModel(BaseModel):
    paper_id: str
    doc_id: str
    display_text: str
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


class PaperSearchResponse(BaseModel):
    # Unique ID for this search, used to look up cache keys in other endpoints
    search_id: str
    # Ordered results returned for the search
    papers: list[PaperModel]
    # True if there are no more results available for a next page
    isEnd: bool
    # True if query is as a yes/no question, None if classifier was not run
    isYesNoQuestion: Optional[bool] = None
    # True if query is as a question, None if classifier was not run
    canSynthesize: Optional[bool] = None
    # True if we allow synthesis on the query, None if classifier was not run
    nuanceRequired: Optional[bool] = None
    # True if some form of synthesis will succeed, None if logic was not run
    canSynthesizeSucceed: Optional[bool] = None
    # Number of total top results, above or below relevancy threshold
    numTopResults: Optional[int] = None
    # Number of results above the relevancy threshold
    numRelevantResults: Optional[int] = None
