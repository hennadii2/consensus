from functools import partial
from typing import Any, Callable, Optional, cast
from urllib.parse import parse_qs, urlencode

import redis
from claim_pb2 import Claim
from common.cache.cache_util import (
    Cache,
    CacheWithDefault,
    read_from_cache,
    read_from_cache_with_default,
    write_to_cache,
)
from common.models.baseten.answer_extractor import MODEL_VERSION_ANSWER_EXTRACTOR
from common.models.offensive_query_classifier import MODEL_VERSION_OFFENSIVE_QUERY
from common.models.openai.question_summarizer import (
    FALLBACK_MODEL_VERSION_QUESTION_SUMMARIZER,
    MODEL_VERSION_QUESTION_SUMMARIZER,
)
from common.models.openai.study_details import MODEL_VERSION_STUDY_DETAILS
from common.models.query_classifier import MODEL_VERSION_QUERY_CLASSIFIER
from common.models.query_expander import MODEL_VERSION_QUERY_EXPANDER
from common.models.question_answer_ranker import MODEL_VERSION_SEARCH_RANKER
from common.models.study_type_classifier import MODEL_VERSION_STUDY_TYPE
from common.models.yes_no_answer_classifier import MODEL_VERSION_YES_NO_ANSWER
from common.search.data import PaperResult
from pydantic import BaseModel, validator
from web.backend.app.common.disputed import DisputedData
from web.backend.app.common.encode_model import decode, encode
from web.backend.app.endpoints.claims.details.data import ClaimDetailsResponse
from web.backend.app.endpoints.paper_search.data import PaperSearchResponse
from web.backend.app.endpoints.papers.details.data import PaperDetailsResponse
from web.backend.app.endpoints.search.data import SearchResponse
from web.backend.app.endpoints.study_details.data import StudyDetailsResponse
from web.backend.app.endpoints.summary.data import SummaryResponse
from web.backend.app.endpoints.yes_no.data import YesNoResponse

GLOBAL_CACHE_BREAKER = "10"


def _remove_key_from_url(full_url: str, key_to_remove: str) -> str:
    parsed_url = parse_qs(full_url)
    if key_to_remove in parsed_url:
        del parsed_url[key_to_remove]
        return urlencode(parsed_url, doseq=True)
    else:
        return full_url


class SearchCacheId(BaseModel):
    id: str


def encode_search_cache_id(id: SearchCacheId, obfuscation_encrypt_key: str) -> str:
    return encode(key=obfuscation_encrypt_key, data=id)


def decode_search_cache_id(encoded_id: str, obfuscation_encrypt_key: str) -> SearchCacheId:
    return decode(
        key=obfuscation_encrypt_key,
        encoded=encoded_id,
        model=SearchCacheId,
    )


def init_search_response_cache(
    full_url: str,
    search_index_id: str,
    disputed: DisputedData,
    page: Optional[int],
    cache_off: Optional[bool],
) -> tuple[Optional[Cache[SearchResponse]], SearchCacheId]:
    """Search endpoint response cache"""
    dependent_models = f"{MODEL_VERSION_SEARCH_RANKER}:{MODEL_VERSION_QUERY_CLASSIFIER}:{MODEL_VERSION_OFFENSIVE_QUERY}:{MODEL_VERSION_QUERY_EXPANDER}"  # noqa: E501
    search_url = _remove_key_from_url(full_url=full_url, key_to_remove="page")
    search_cache_id = SearchCacheId(
        id=f"{search_url}:{search_index_id}:{disputed.version}:{dependent_models}:{GLOBAL_CACHE_BREAKER}:5"  # noqa: E501
    )
    if cache_off:
        return (None, search_cache_id)

    cache_key = f"search_response:{search_cache_id.id}:{page}:6"
    read = cast(
        Callable[[redis.Redis], Optional[SearchResponse]],
        partial(read_from_cache, cache_key, SearchResponse),
    )
    write = partial(write_to_cache, cache_key)
    return (Cache[SearchResponse](read=read, write=write), search_cache_id)


def init_paper_search_response_cache(
    full_url: str,
    search_index_name: str,
    disputed: DisputedData,
    page: Optional[int],
    cache_off: Optional[bool],
) -> tuple[Optional[Cache[PaperSearchResponse]], SearchCacheId]:
    """Search endpoint response cache"""
    dependent_models = f"{MODEL_VERSION_SEARCH_RANKER}:{MODEL_VERSION_QUERY_CLASSIFIER}:{MODEL_VERSION_OFFENSIVE_QUERY}:{MODEL_VERSION_QUERY_EXPANDER}:{MODEL_VERSION_ANSWER_EXTRACTOR}"  # noqa: E501
    search_url = _remove_key_from_url(full_url=full_url, key_to_remove="page")
    search_cache_id = SearchCacheId(
        id=f"{search_url}:{search_index_name}:{disputed.version}:{dependent_models}:{GLOBAL_CACHE_BREAKER}:7"  # noqa: E501
    )
    if cache_off:
        return (None, search_cache_id)

    cache_key = f"search_response:{search_cache_id.id}:{page}:4"
    read = cast(
        Callable[[redis.Redis], Optional[PaperSearchResponse]],
        partial(read_from_cache, cache_key, PaperSearchResponse),
    )
    write = partial(write_to_cache, cache_key)
    return (Cache[PaperSearchResponse](read=read, write=write), search_cache_id)


def init_yes_no_response_cache(
    full_url: str,
    disputed: DisputedData,
) -> Cache[YesNoResponse]:
    """Yes/No endpoint response cache"""
    dependent_models = (
        f"{MODEL_VERSION_YES_NO_ANSWER}:{MODEL_VERSION_OFFENSIVE_QUERY}"  # noqa: E501
    )
    cache_key = f"yes_no:{full_url}:{dependent_models}:{disputed.version}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E501
    read = cast(
        Callable[[redis.Redis], Optional[YesNoResponse]],
        partial(read_from_cache, cache_key, YesNoResponse),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[YesNoResponse](read=read, write=write)


def init_summary_response_cache(
    full_url: str,
    disputed: DisputedData,
) -> Cache[SummaryResponse]:
    """Summary endpoint response cache"""
    dependent_models = (
        f"{MODEL_VERSION_QUESTION_SUMMARIZER}:{MODEL_VERSION_OFFENSIVE_QUERY}"  # noqa: E501
    )
    cache_key = f"summary:{full_url}:{dependent_models}:{disputed.version}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E501
    read = cast(
        Callable[[redis.Redis], Optional[SummaryResponse]],
        partial(read_from_cache, cache_key, SummaryResponse),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[SummaryResponse](read=read, write=write)


class FallbackSummary(BaseModel):
    summary: Optional[str]


def init_fallback_summary_cache(
    search_cache_id: SearchCacheId,
) -> Cache[FallbackSummary]:
    """Summary endpoint response cache"""
    dependent_models = f"{FALLBACK_MODEL_VERSION_QUESTION_SUMMARIZER}"  # noqa: E501
    cache_key = f"fallback_summary:{search_cache_id.id}:{dependent_models}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E501
    read = cast(
        Callable[[redis.Redis], Optional[FallbackSummary]],
        partial(read_from_cache, cache_key, FallbackSummary),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[FallbackSummary](read=read, write=write)


def init_study_details_response_cache(
    full_url: str,
) -> Cache[StudyDetailsResponse]:
    """Study details endpoint response cache"""
    dependent_models = f"{MODEL_VERSION_STUDY_DETAILS}"  # noqa: E501
    cache_key = (
        f"study_details:{full_url}:{dependent_models}:{GLOBAL_CACHE_BREAKER}:4"  # noqa: E501
    )
    read = cast(
        Callable[[redis.Redis], Optional[StudyDetailsResponse]],
        partial(read_from_cache, cache_key, StudyDetailsResponse),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[StudyDetailsResponse](read=read, write=write)


def init_claim_details_response_cache(
    full_url: str,
    disputed: DisputedData,
) -> Cache[ClaimDetailsResponse]:
    """Claim details endpoint response cache"""
    dependent_models = f"{MODEL_VERSION_STUDY_TYPE}"
    cache_key = f"claim_details:{full_url}:{dependent_models}:{disputed.version}:{GLOBAL_CACHE_BREAKER}:4"  # noqa: E50
    read = cast(
        Callable[[redis.Redis], Optional[ClaimDetailsResponse]],
        partial(read_from_cache, cache_key, ClaimDetailsResponse),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[ClaimDetailsResponse](read=read, write=write)


def init_paper_details_response_cache(
    full_url: str,
    disputed: DisputedData,
) -> Cache[PaperDetailsResponse]:
    """Paper details endpoint response cache"""
    dependent_models = f"{MODEL_VERSION_STUDY_TYPE}"
    cache_key = f"paper_details:{full_url}:{dependent_models}:{disputed.version}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E50
    read = cast(
        Callable[[redis.Redis], Optional[PaperDetailsResponse]],
        partial(read_from_cache, cache_key, PaperDetailsResponse),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[PaperDetailsResponse](read=read, write=write)


class QueryResultData(BaseModel):
    id: str
    paper_id: str
    text: str

    @validator("paper_id", pre=True)
    def validate_paper_id(cls, v: Any) -> str:
        return str(v)


def claim_proto_to_query_result_data(claim: Claim) -> QueryResultData:
    return QueryResultData(
        id=claim.id,
        paper_id=claim.paper_id,
        text=claim.metadata.text,
    )


def paper_result_to_query_result_data(paper: PaperResult) -> QueryResultData:
    return QueryResultData(
        id=paper.hash_paper_id,
        paper_id=paper.paper_id,
        text=paper.display_text if paper.display_text is not None else "",
    )


class QueryResults(BaseModel):
    results: list[QueryResultData]


def init_query_result_data_cache(
    result_ids: str,
) -> Cache[QueryResults]:
    """Minimal search result data for a set of result ids"""
    cache_key = f"query_result_data:{result_ids}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E501
    read = cast(
        Callable[[redis.Redis], Optional[QueryResults]],
        partial(read_from_cache, cache_key, QueryResults),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[QueryResults](read=read, write=write)


class QueryFeatures(BaseModel):
    is_synthesizable: Optional[bool]
    is_yes_no_question: Optional[bool]
    is_offensive: Optional[bool]


class TopQueryResults(BaseModel):
    results: list[QueryResultData]
    relevance_scores: list[float]
    query: str
    query_features: QueryFeatures


def init_top_query_results_cache(
    search_cache_id: SearchCacheId,
) -> Cache[TopQueryResults]:
    """
    Top X ranked results for a search.

    Generated in search and used downstream in models based on top results.
    """
    cache_key = f"top_query_results:{search_cache_id.id}:{GLOBAL_CACHE_BREAKER}:2"  # noqa: E501
    read = cast(
        Callable[[redis.Redis], Optional[TopQueryResults]],
        partial(read_from_cache, cache_key, TopQueryResults),
    )
    write = partial(write_to_cache, cache_key)
    return Cache[TopQueryResults](read=read, write=write)


class UsedPaperIds(BaseModel):
    ids: dict[str, bool]

    @validator("ids", pre=True)
    def validate_paper_id(cls, v: Any) -> dict[str, bool]:
        if isinstance(v, dict):
            if not len(v.keys()):
                return v
            if isinstance(list(v.keys())[0], str):
                return v
            v_with_str_keys: dict[str, bool] = {}
            for key, value in v.items():
                str_key = str(key)
                v_with_str_keys[str_key] = value
            return v_with_str_keys
        else:
            raise ValueError(f"used_paper_ids must be dict, not {type(v)}")


def init_used_paper_ids_cache(
    search_cache_id: SearchCacheId,
    page: Optional[int],
) -> CacheWithDefault[UsedPaperIds]:
    """Paper ids are cached to skip returning multiple claims from the same paper"""
    base_cache_key = f"used_paper_ids:{search_cache_id.id}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E501
    cache_key_to_read = None if page == 0 else f"{base_cache_key}:{page}"

    next_page = 0 if page is None else page + 1
    cache_key_to_write = f"{base_cache_key}:{next_page}"

    read = cast(
        Callable[[redis.Redis], UsedPaperIds],
        partial(
            read_from_cache_with_default,
            cache_key_to_read,
            UsedPaperIds,
            UsedPaperIds(ids={}),
        ),
    )
    write = partial(write_to_cache, cache_key_to_write)
    return CacheWithDefault[UsedPaperIds](read=read, write=write)


class UsedAnswers(BaseModel):
    hashes: dict[int, bool]


def init_used_answers_cache(
    search_cache_id: SearchCacheId,
    page: Optional[int],
) -> CacheWithDefault[UsedAnswers]:
    """Paper answers are cached to skip returning multiple answers from the same paper"""
    base_cache_key = f"used_answers:{search_cache_id.id}:{GLOBAL_CACHE_BREAKER}:1"  # noqa: E501
    cache_key_to_read = None if page == 0 else f"{base_cache_key}:{page}"

    next_page = 0 if page is None else page + 1
    cache_key_to_write = f"{base_cache_key}:{next_page}"

    read = cast(
        Callable[[redis.Redis], UsedAnswers],
        partial(
            read_from_cache_with_default,
            cache_key_to_read,
            UsedAnswers,
            UsedAnswers(hashes={}),
        ),
    )
    write = partial(write_to_cache, cache_key_to_write)
    return CacheWithDefault[UsedAnswers](read=read, write=write)
