from enum import Enum
from typing import Optional

from pydantic import BaseModel
from web.backend.app.common.data import (
    MAX_DISPUTED_RESULTS_PERCENTAGE_THRESHOLD,
    MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS,
)

MOCK_SUMMARY = "Mock Summary"

MIN_RELEVANCY_THRESHOLD = MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS
MAX_DISPUTED_PERCENTAGE_THRESHOLD = MAX_DISPUTED_RESULTS_PERCENTAGE_THRESHOLD
MIN_NUMBER_RESULTS_TO_SUMMARIZE = 2
MAX_NUMBER_RESULTS_TO_SUMMARIZE = 10

LOG_ENDPOINT = "summary"


class LOG_EVENTS(Enum):
    LOAD_FROM_CACHE = "load_from_cache"
    READ_RESULTS = "read_results"
    RUN_QUESTION_SUMMARIZER = "question_summarizer"
    RUN_FALLBACK_QUESTION_SUMMARIZER = "fallback_question_summarizer"
    LOAD_FALLBACK_SUMMARY_FROM_CACHE = "load_fallback_summary_from_cache"
    CREATE_RESPONSE = "create_response"


class SummaryResponse(BaseModel):
    """
    A response from the /summary endpoint.
    """

    # Summary text if it completed
    summary: Optional[str]
    # Number of results analyzed
    resultsAnalyzedCount: int
    # True if there were not enough relevant claims to run classifier
    isIncomplete: bool
    # True if there were enough disputed claims for a warning
    isDisputed: bool
    # True if the daily limit of summarizations was reached
    dailyLimitReached: bool
