from dataclasses import dataclass
from random import randint


def make_query(
    text: str,
    exact_match: bool,
) -> dict:
    """
    Returns a keyword search query configured by the given parameters.
    """

    if exact_match:
        # Match the query terms in exact order only
        return {"match_phrase_prefix": {"text": text}}
    else:
        # Matches the query terms in any order, but scores documents higher if
        # they container terms in order in a shingle subfield.
        return {
            "multi_match": {
                "query": text,
                "fuzziness": "AUTO",
                "type": "bool_prefix",
                "fields": ["text", "text._2gram", "text._3gram", "text._4gram"],
            },
        }


def make_random_select_query() -> dict:
    """
    Returns a search query to select a random set of claims.
    """
    return {
        "script_score": {
            "query": {
                "match_all": {},
            },
            "script": {"source": f"randomScore({randint(0, 1000)})"},
        }
    }


@dataclass(frozen=True)
class Suggestion:
    key: str
    query: dict


def make_spelling_suggest(
    text: str,
) -> Suggestion:
    return Suggestion(
        key="spelling", query={"spelling": {"text": text, "term": {"field": "text"}}}
    )


@dataclass(frozen=True)
class CompletionSuggest:
    key: str
    query: dict


def make_completion_suggest(
    text: str,
) -> Suggestion:
    return Suggestion(
        key="query-suggest",
        query={
            "query-suggest": {
                "prefix": text,
                "completion": {
                    "field": "text",
                    "fuzzy": {"fuzziness": "auto"},
                    "skip_duplicates": True,
                },
            }
        },
    )
