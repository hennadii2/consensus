from typing import Optional

import redis
from common.logging.timing import time_endpoint_event
from common.models.openai.question_summarizer import (
    create_summarize_question_gpt4_input,
    summarize_question_davinci,
    summarize_question_gpt4_with_backoff,
)
from web.backend.app.common.cache import (
    FallbackSummary,
    SearchCacheId,
    init_fallback_summary_cache,
)
from web.backend.app.endpoints.summary.data import LOG_ENDPOINT, LOG_EVENTS


async def summarize_with_fallback(
    redis: redis.Redis,
    search_cache_id: SearchCacheId,
    question: str,
    answers: list[str],
) -> tuple[Optional[str], bool]:
    """
    Tries GPT-4 endpoint for summary with exponential backoff. If it ultimately
    fails, calls davinci model as a final effort.
    """
    try:
        log_run_question_summarizer = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.RUN_QUESTION_SUMMARIZER.value,
        )
        gpt4_input = create_summarize_question_gpt4_input(question=question, answers=answers)
        gpt4_summary = await summarize_question_gpt4_with_backoff(input=gpt4_input)
        log_run_question_summarizer()
        return (gpt4_summary.summary, True)
    except Exception:
        log_load_fallback_summary_from_cache = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FALLBACK_SUMMARY_FROM_CACHE.value,
        )
        fallback_cache = init_fallback_summary_cache(search_cache_id=search_cache_id)
        cached_fallback_summary = fallback_cache.read(redis)
        if cached_fallback_summary is not None:
            log_load_fallback_summary_from_cache()
            return (cached_fallback_summary.summary, False)

        log_run_fallback_question_summarizer = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.RUN_FALLBACK_QUESTION_SUMMARIZER.value,
        )
        davinci_summary = await summarize_question_davinci(question=question, answers=answers)
        fallback_cache.write(redis, FallbackSummary(summary=davinci_summary.summary))
        log_run_fallback_question_summarizer()
        return (davinci_summary.summary, False)
