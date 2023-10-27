from typing import Optional

from common.search.autocomplete_index import AutocompleteIndex
from fastapi import APIRouter, Request
from loguru import logger
from nltk.corpus import stopwords
from pydantic import BaseModel
from web.backend.app.state import SharedState

router = APIRouter()

NUMBER_OF_SUGGESTIONS = 5


class AutocompleteResponse(BaseModel):
    """
    A response from the /autocomplete endpoint.
    """

    queries: list[str]


@router.get("/", response_model=AutocompleteResponse)
def autocomplete(
    request: Request,
    query: str,
    autocomplete_exact_match: Optional[bool] = None,
    autocomplete_exact_match_better: Optional[bool] = None,
    autocomplete_spelling: Optional[bool] = None,
    autocomplete_preferred_boost: Optional[float] = None,
    autocomplete_preferred_only: Optional[bool] = None,
    autocomplete_switch_to_exact: Optional[int] = None,
    autocomplete_switch_to_exact_words: Optional[int] = None,
    autocomplete_remove_space: Optional[bool] = None,
    autocomplete_add_space: Optional[bool] = None,
    autocomplete_words_boost: Optional[float] = None,
):
    shared: SharedState = request.app.state.shared
    if shared.config.autocomplete_index_id is None:
        return AutocompleteResponse(queries=[])

    autocomplete_index = AutocompleteIndex(
        es=shared.es,
        index_id=shared.config.autocomplete_index_id,
    )

    # Setup defaults
    autocomplete_words_boost = (
        autocomplete_words_boost if autocomplete_words_boost is not None else 50
    )
    autocomplete_preferred_boost = (
        autocomplete_preferred_boost if autocomplete_preferred_boost is not None else 3
    )
    autocomplete_switch_to_exact_words = (
        autocomplete_switch_to_exact_words if autocomplete_switch_to_exact_words is not None else 3
    )
    autocomplete_remove_space = (
        autocomplete_remove_space if autocomplete_remove_space is not None else True
    )

    try:
        if len(query) == 0:
            queries = autocomplete_index.get_random_preferred_queries(size=NUMBER_OF_SUGGESTIONS)
            return AutocompleteResponse(queries=queries)

        if autocomplete_exact_match_better:
            queries = autocomplete_index.suggest_queries_completion(
                text=query,
                size=NUMBER_OF_SUGGESTIONS,
                preferred_only=autocomplete_preferred_only,
            )
            return AutocompleteResponse(queries=queries)
        else:
            exact_match = False if autocomplete_exact_match is None else autocomplete_exact_match
            if not exact_match and autocomplete_switch_to_exact is not None:
                exact_match = len(query) >= autocomplete_switch_to_exact
            elif not exact_match and autocomplete_switch_to_exact_words is not None:
                exact_match = len(query.split()) >= autocomplete_switch_to_exact_words

            if not exact_match and autocomplete_words_boost is not None:
                ends_with_space = query.endswith(" ")
                words = query.split()
                boosts = [
                    ""
                    if x.lower() in stopwords.words("english")
                    else f"^{autocomplete_words_boost}"
                    for x in words
                ]
                if len(words[-1]) < 4:
                    boosts[-1] = ""
                assert len(boosts) == len(words)
                query = " ".join([f"{words[i]}{boosts[i]}" for i in range(len(words))])
                query = query if not ends_with_space else f"{query} "

            if autocomplete_remove_space:
                query = query.strip()
            elif autocomplete_add_space:
                query = query.strip() + " "

            queries = autocomplete_index.suggest_queries(
                text=query,
                size=NUMBER_OF_SUGGESTIONS,
                exact_match=exact_match,
                with_spelling=False if autocomplete_spelling is None else autocomplete_spelling,
                preferred_boost=autocomplete_preferred_boost,
                preferred_only=autocomplete_preferred_only,
            )
            return AutocompleteResponse(queries=queries)
    except Exception as e:
        # Autocomplete is best effort, so log an error but return valid response
        logger.info(e)
        return AutocompleteResponse(queries=[])
