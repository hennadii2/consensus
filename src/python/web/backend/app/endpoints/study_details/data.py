from enum import Enum
from typing import Optional

from pydantic import BaseModel

LOG_ENDPOINT = "study_details"


class LOG_EVENTS(Enum):
    LOAD_FROM_CACHE = "load_from_cache"
    READ_DB = "read_db"
    READ_ABSTRACT = "read_abstract"
    RUN_MODELS = "run_models"


class StudyDetailsResponse(BaseModel):
    """
    A response from the /study_details endpoint.
    """

    # Study details text if it completed
    population: Optional[str]
    method: Optional[str]
    outcome: Optional[str]
    # True if the daily limit of openai calls was reached
    dailyLimitReached: bool
