from common.storage.example_queries import (
    ExampleQueriesData,
    parse_data,
    read_example_queries_text,
)
from fastapi import APIRouter, Request
from loguru import logger
from pydantic import BaseModel
from web.backend.app.state import SharedState

router = APIRouter()

TEMP_HARD_CODED_TRENDING_QUERIES = [
    "are covid-19 vaccines effective?",
    "benefits of mindfulness",
    "direct cash transfers and poverty",
]


class TrendingQueriesResponse(BaseModel):
    """
    A response from the /trending/queries endpoint.
    """

    # The list of queries to display.
    queries: list[str]
    questionTypes: list[ExampleQueriesData]
    topics: list[ExampleQueriesData]
    emptyAutocompleteQueries: list[str]


@router.get("/queries", response_model=TrendingQueriesResponse)
def trending_queries(request: Request):
    """
    Returns a response of trending queries to display on the homepage.
    """
    shared: SharedState = request.app.state.shared

    try:
        example_queries_json = read_example_queries_text(client=shared.storage_client)
        if not example_queries_json:
            raise ValueError("Failed to read example queries from blob store.")

        queries = parse_data(example_queries_json)
        return TrendingQueriesResponse(
            queries=queries.search_bar,
            questionTypes=queries.how_to_search.question_types,
            topics=queries.how_to_search.topics,
            emptyAutocompleteQueries=[]
            if queries.empty_autocomplete is None
            else queries.empty_autocomplete,
        )
    except Exception as e:
        logger.exception(e)
        return TrendingQueriesResponse(
            queries=TEMP_HARD_CODED_TRENDING_QUERIES,
            questionTypes=[],
            topics=[],
            emptyAutocompleteQueries=[],
        )
