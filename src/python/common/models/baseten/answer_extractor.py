from dataclasses import dataclass
from typing import Optional, Tuple

from requests import HTTPError, Session

_BASETEN_MODEL_VERSION_WITH_RERANK = "q417pkq"
_BASETEN_BASE_URL = "https://app.baseten.co/model_versions"

MODEL_VERSION_ANSWER_EXTRACTOR = f"{_BASETEN_MODEL_VERSION_WITH_RERANK}"


@dataclass(frozen=True)
class AnswerExtractor:
    session: Session


def initialize_answer_extractor(baseten_api_key: str) -> AnswerExtractor:
    """
    Initializes baseten API.
    """
    session = Session()
    session.headers.update({"Authorization": f"Api-Key {baseten_api_key}"})

    return AnswerExtractor(session=session)


def extract_answers_with_rank(
    answer_extractor: AnswerExtractor,
    query: str,
    abstracts_by_id: list[Tuple[str, Optional[str]]],
    model_override: Optional[str],
) -> dict[str, Tuple[str, float]]:
    """
    Returns a generated answer for the query from a single abstract
    with QA reranker probability.
    """

    model = _BASETEN_MODEL_VERSION_WITH_RERANK if model_override is None else model_override
    papers_payload = [
        {f"{id}": abstract} for id, abstract in abstracts_by_id if abstract is not None
    ]
    response = answer_extractor.session.post(
        url=f"{_BASETEN_BASE_URL}/{model}/predict",
        json={"user_query": query, "papers": papers_payload},
    )
    if response.status_code != 200:
        raise HTTPError(f"Failed to extract answers: {response.status_code} {response.reason}")

    extracted_answers_with_rank: dict[str, Tuple[str, float]] = response.json()["model_output"]

    return extracted_answers_with_rank
