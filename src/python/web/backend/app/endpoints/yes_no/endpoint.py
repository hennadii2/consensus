from typing import Optional, cast

from common.logging.timing import time_endpoint_event
from common.models.offensive_query_classifier import is_query_offensive
from common.models.yes_no_answer_classifier import YesNoAnswerInput
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.cache import (
    QueryResultData,
    decode_search_cache_id,
    init_top_query_results_cache,
    init_yes_no_response_cache,
)
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.endpoints.yes_no.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    MAX_DISPUTED_PERCENTAGE_THRESHOLD,
    MIN_NUMBER_RESULTS_TO_RUN_YES_NO,
    MIN_RESULT_RELEVANCY_THRESHOLD,
    YesNoResponse,
)
from web.backend.app.endpoints.yes_no.util import EMPTY_ANSWERS, create_yes_no_response
from web.backend.app.state import SharedState
from web.services.api import predict_yes_no_answers

router = APIRouter()


@router.get("/", response_model=YesNoResponse)
async def yes_no(
    request: Request,
    # Search ID for results to analyze, returned from /search endpoint
    search_id: str,
    # #####################
    # Testing parameters
    # #####################
    # Testing param: Min relevancy threshold to include result in the meter
    synthesize_threshold: Optional[float] = None,
    # Testing param: Min probability threshold to include an answer in the meter
    meter_answer_threshold: Optional[float] = None,
    # Testing param: Run meter regardless of offensive query result
    meter_force_run: Optional[bool] = None,
    # Testing param: skip cache
    cache_off: Optional[bool] = None,
):
    """
    Runs the yes/no classifier on a query and a set of answers and returns the results.
    """
    shared: SharedState = request.app.state.shared
    disputed = parse_disputed_data(storage_client=shared.storage_client)

    # Try to load yes/no response from cache
    yes_no_response_cache = (
        None
        if cache_off
        else init_yes_no_response_cache(
            full_url=str(request.url),
            disputed=disputed,
        )
    )
    if yes_no_response_cache is not None:
        log_load_from_cache_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FROM_CACHE.value,
        )
        cached_yes_no_response = yes_no_response_cache.read(shared.redis)
        if cached_yes_no_response is not None:
            log_load_from_cache_event()
            return cached_yes_no_response

    try:
        if shared.services is None:
            raise ValueError("Yes/No classifier model is not initialized.")

        search_cache_id = decode_search_cache_id(
            encoded_id=search_id,
            obfuscation_encrypt_key=shared.config.obfuscation_encrypt_key,
        )
        top_results_cache = init_top_query_results_cache(search_cache_id)
        top_results = top_results_cache.read(shared.redis)
        if top_results is None:
            raise ValueError(f"Top results not in cache: {search_cache_id}")

        if shared.models.offensive_query_classifier is not None:
            log_offensive_query_classifier_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.OFFENSIVE_QUERY_CLASSIFIER.value,
            )
            is_offensive_query = (
                False
                if meter_force_run
                else is_query_offensive(
                    model=shared.models.offensive_query_classifier,
                    query=top_results.query,
                )
            )
            log_offensive_query_classifier_timing_event()
            if is_offensive_query:
                return YesNoResponse(
                    resultsAnalyzedCount=0,
                    yesNoAnswerPercents=EMPTY_ANSWERS,
                    resultIdToYesNoAnswer={},
                    isDisputed=False,
                    isIncomplete=False,
                    isSkipped=True,
                )

        log_read_results_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_RESULTS.value,
        )
        min_synthesize_threshold = (
            synthesize_threshold
            if synthesize_threshold is not None
            else MIN_RESULT_RELEVANCY_THRESHOLD
        )
        assert len(top_results.results) == len(top_results.relevance_scores)
        query_results: list[QueryResultData] = [
            top_results.results[i]
            for i in range(len(top_results.results))
            if top_results.relevance_scores[i] >= min_synthesize_threshold
        ]
        log_read_results_event()

        log_answer_classifier_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.ANSWER_CLASSIFIER.value,
        )
        yes_no_inputs = [cast(YesNoAnswerInput, result.dict()) for result in query_results]
        yes_no_answer_response = await predict_yes_no_answers(
            cxn=shared.services,
            inputs=yes_no_inputs,
            query=top_results.query,
            min_probability_threshold=meter_answer_threshold,
        )
        log_answer_classifier_event()

        log_create_response_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.CREATE_RESPONSE.value,
        )
        yes_no_response = create_yes_no_response(
            yes_no_inputs=yes_no_inputs,
            yes_no_predictions=yes_no_answer_response.predictions,
            min_num_results_with_answers_threshold=MIN_NUMBER_RESULTS_TO_RUN_YES_NO,
            disputed=disputed,
            max_percent_disputed_threshold=MAX_DISPUTED_PERCENTAGE_THRESHOLD,
        )
        log_create_response_event()

        if yes_no_response_cache is not None:
            yes_no_response_cache.write(shared.redis, yes_no_response)

        return yes_no_response
    except Exception as e:
        logger.exception(f"Failed to run yes_no classifier for: {search_id}")
        raise HTTPException(status_code=500, detail=str(e))
