from enum import Enum
from typing import Optional

from pydantic import BaseModel
from web.backend.app.common.data import (
    MAX_DISPUTED_RESULTS_PERCENTAGE_THRESHOLD,
    MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS,
)

MIN_RESULT_RELEVANCY_THRESHOLD = MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS
MAX_DISPUTED_PERCENTAGE_THRESHOLD = MAX_DISPUTED_RESULTS_PERCENTAGE_THRESHOLD
MIN_NUMBER_RESULTS_TO_RUN_YES_NO = 5


LOG_ENDPOINT = "yes_no"


class LOG_EVENTS(Enum):
    LOAD_FROM_CACHE = "load_from_cache"
    READ_RESULTS = "read_results"
    ANSWER_CLASSIFIER = "yes_no_answer_classifier"
    CREATE_RESPONSE = "create_response"
    OFFENSIVE_QUERY_CLASSIFIER = "offensive_query_classifier"


class AnswerPercents(BaseModel):
    YES: int
    NO: int
    POSSIBLY: int


class YesNoResponse(BaseModel):
    """
    A response from the /yes_no endpoint.
    """

    # Number of results analyzed
    resultsAnalyzedCount: int
    # Map of answers to their percents
    yesNoAnswerPercents: AnswerPercents
    # Map of result ids to their answer
    resultIdToYesNoAnswer: Optional[dict[str, str]]
    # True if there were not enough relevant results to run classifier
    isIncomplete: bool
    # True if there were enough disputed results for a warning
    isDisputed: bool
    # True if the query was not run through yesNo
    isSkipped: bool
