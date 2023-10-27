from typing import Optional

from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.cache import (
    QueryResultData,
    decode_search_cache_id,
    init_summary_response_cache,
    init_top_query_results_cache,
)
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.common.rate_limit_openai import denied_by_daily_cost_limit
from web.backend.app.common.util import percent_true
from web.backend.app.endpoints.summary.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    MAX_DISPUTED_PERCENTAGE_THRESHOLD,
    MAX_NUMBER_RESULTS_TO_SUMMARIZE,
    MIN_NUMBER_RESULTS_TO_SUMMARIZE,
    MIN_RELEVANCY_THRESHOLD,
    MOCK_SUMMARY,
    SummaryResponse,
)
from web.backend.app.endpoints.summary.util import summarize_with_fallback
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/", response_model=SummaryResponse)
async def summary(
    request: Request,
    # Search ID for results to analyze, returned from /search endpoint
    search_id: str,
    # #####################
    # Testing parameters
    # #####################
    # Testing param: max number of results to include in summary
    summary_max_results: Optional[int] = None,
    # Testing param: skip cache
    cache_off: Optional[bool] = None,
    # Testing param: override for daily limit of openai calls
    summary_daily_limit: Optional[int] = None,
    # Testing param: Min relevancy threshold to include results in the summary
    synthesize_threshold: Optional[float] = None,
):
    """
    Runs a summarizer on a query and a set of search results and returns the summary.
    """
    shared: SharedState = request.app.state.shared
    disputed = parse_disputed_data(storage_client=shared.storage_client)

    # Try to load response from cache
    summary_response_cache = (
        None
        if cache_off
        else init_summary_response_cache(
            full_url=str(request.url),
            disputed=disputed,
        )
    )
    if summary_response_cache is not None:
        log_load_from_cache_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FROM_CACHE.value,
        )
        cached_summary_response = summary_response_cache.read(shared.redis)
        if cached_summary_response is not None:
            log_load_from_cache_event()
            return cached_summary_response

    try:
        if denied_by_daily_cost_limit(redis=shared.redis, daily_limit=summary_daily_limit):
            return SummaryResponse(
                summary=None,
                resultsAnalyzedCount=0,
                isIncomplete=False,
                isDisputed=False,
                dailyLimitReached=True,
            )

        if not shared.models.is_openai_initialized and not shared.config.is_local_env:
            raise ValueError("Summarizer is not initialized.")

        search_cache_id = decode_search_cache_id(
            encoded_id=search_id,
            obfuscation_encrypt_key=shared.config.obfuscation_encrypt_key,
        )
        top_results_cache = init_top_query_results_cache(search_cache_id)
        top_results = top_results_cache.read(shared.redis)
        if top_results is None:
            raise ValueError(f"Top results not in cache: {search_cache_id}")

        log_read_results_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_RESULTS.value,
        )
        min_synthesize_threshold = (
            synthesize_threshold if synthesize_threshold is not None else MIN_RELEVANCY_THRESHOLD
        )
        assert len(top_results.results) == len(top_results.relevance_scores)
        query_results: list[QueryResultData] = [
            result
            for result, relevancy_score in zip(top_results.results, top_results.relevance_scores)
            if relevancy_score >= min_synthesize_threshold
        ]
        log_read_results_event()

        is_incomplete = len(query_results) < MIN_NUMBER_RESULTS_TO_SUMMARIZE
        max_num_results = (
            summary_max_results
            if summary_max_results is not None
            else MAX_NUMBER_RESULTS_TO_SUMMARIZE
        )

        summary = None
        should_cache_response = False
        results_analyzed_count = 0
        if not is_incomplete:
            if shared.config.is_local_env and not shared.models.is_openai_initialized:
                summary = MOCK_SUMMARY
            else:
                answers = [result.text for result in query_results[:max_num_results]]
                summary, should_cache_response = await summarize_with_fallback(
                    redis=shared.redis,
                    search_cache_id=search_cache_id,
                    question=top_results.query,
                    answers=answers,
                )
                results_analyzed_count = len(answers)
                is_incomplete = summary is None

        is_disputed = (
            False
            if is_incomplete
            else percent_true(
                query_results, lambda x: x.paper_id in disputed.disputed_badges_by_paper_id
            )
            >= MAX_DISPUTED_PERCENTAGE_THRESHOLD
        )
        summary_response = SummaryResponse(
            summary=summary,
            resultsAnalyzedCount=0 if is_incomplete else results_analyzed_count,
            isIncomplete=is_incomplete,
            isDisputed=is_disputed,
            dailyLimitReached=False,
        )

        if summary_response_cache is not None and should_cache_response:
            summary_response_cache.write(shared.redis, summary_response)

        return summary_response
    except Exception as e:
        logger.exception(f"Failed to run summarizer for: {search_id}")
        raise HTTPException(status_code=500, detail=str(e))
