import asyncio
from typing import Optional

from common.db.hash_paper_ids import HashPaperIds
from common.db.papers import Papers
from common.logging.timing import time_endpoint_event
from common.models.openai.study_details import (
    StudyDetailsType,
    create_study_details_gpt4_input,
    generate_study_details_gpt4_with_backoff,
)
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.async_wrappers import read_abstract, read_paper, read_paper_id
from web.backend.app.common.cache import init_study_details_response_cache
from web.backend.app.common.rate_limit_openai import denied_by_daily_cost_limit
from web.backend.app.endpoints.study_details.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    StudyDetailsResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/{hash_paper_id}", response_model=StudyDetailsResponse)
async def study_details(
    request: Request,
    hash_paper_id: str,
    # #####################
    # Testing parameters
    # #####################
    # Testing param: skip cache
    cache_off: Optional[bool] = None,
):
    """
    Runs a study details prompt on an abstract and returns the results.
    """
    shared: SharedState = request.app.state.shared

    db = shared.db()
    papers = Papers(db.connection, use_v2=shared.config.use_papers_v2)
    hash_paper_ids = HashPaperIds(db.connection)

    # Try to load response from cache
    response_cache = (
        None
        if cache_off
        else init_study_details_response_cache(
            full_url=str(request.url),
        )
    )
    if response_cache is not None:
        log_load_from_cache_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FROM_CACHE.value,
        )
        cached_response = response_cache.read(shared.redis)
        if cached_response is not None:
            log_load_from_cache_event()
            return cached_response

    try:
        if denied_by_daily_cost_limit(redis=shared.redis):
            return StudyDetailsResponse(
                population=None,
                method=None,
                outcome=None,
                dailyLimitReached=True,
            )

        if not shared.models.is_openai_initialized and not shared.config.is_local_env:
            raise ValueError("Study details is not initialized.")

        log_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )
        # TODO(meganvw): Write join SQL query to directly read_paper by hash_paper_id.
        paper_id = await read_paper_id(hash_paper_ids, hash_paper_id)
        if paper_id is None:
            raise ValueError(f"Failed to get paper details: paper id not found: {hash_paper_id}")
        paper = await read_paper(papers=papers, paper_id=paper_id)
        if paper is None:
            raise ValueError(f"Failed to get study details: paper not found: {paper_id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_ABSTRACT.value,
        )
        abstract = await read_abstract(
            storage_client=shared.storage_client,
            paper=paper,
        )
        if abstract is None:
            raise ValueError(f"Failed to get study details: abstract not found: {paper_id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.RUN_MODELS.value,
        )
        MODELS_TO_RUN = [
            StudyDetailsType.POPULATION,
            StudyDetailsType.METHOD,
            StudyDetailsType.OUTCOME,
        ]
        inputs = {x: create_study_details_gpt4_input(x, abstract=abstract) for x in MODELS_TO_RUN}
        results = await asyncio.gather(
            *[generate_study_details_gpt4_with_backoff(inputs[x]) for x in MODELS_TO_RUN]
        )
        study_details = {model_type: result for model_type, result in zip(MODELS_TO_RUN, results)}
        log_timing_event()

        response = StudyDetailsResponse(
            population=study_details[StudyDetailsType.POPULATION].details,
            method=study_details[StudyDetailsType.METHOD].details,
            outcome=study_details[StudyDetailsType.OUTCOME].details,
            dailyLimitReached=False,
        )

        if response_cache is not None:
            response_cache.write(shared.redis, response)

        return response
    except Exception as e:
        logger.exception(f"Failed to run study details for: {hash_paper_id}")
        raise HTTPException(status_code=500, detail=str(e))
