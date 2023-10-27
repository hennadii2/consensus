from typing import Optional

from common.logging.timing import time_endpoint_event
from common.models.offensive_query_classifier import is_query_offensive
from common.models.query_classifier import is_query_synthesizable
from common.models.yes_no_question_classifier import is_query_a_yes_no_question
from web.backend.app.common.cache import QueryFeatures
from web.backend.app.endpoints.search.data import LOG_ENDPOINT, LOG_EVENTS
from web.backend.app.state import SharedState


def analyze_query(
    query: str,
    shared: SharedState,
    enable_yes_no: Optional[bool],
    enable_summary: Optional[bool],
    use_v2: bool,
) -> QueryFeatures:
    """Runs relevant analyzers on query."""
    is_synthesizable = None
    if enable_summary and shared.models.query_classifier is not None:
        log_query_classifier_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.QUERY_CLASSIFIER.value,
        )
        is_synthesizable = is_query_synthesizable(
            classifier=shared.models.query_classifier,
            query=query,
            use_v2=use_v2,
        )
        log_query_classifier_event()

    is_yes_no_question = None
    if enable_yes_no and shared.models.yes_no_question_classifier is not None:
        if is_synthesizable is not None and not is_synthesizable:
            is_yes_no_question = False
        else:
            log_yes_no_classifier_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.YES_NO_CLASSIFIER.value,
            )
            is_yes_no_question = is_query_a_yes_no_question(
                classifier=shared.models.yes_no_question_classifier,
                query=query,
            )
            log_yes_no_classifier_event()

    is_offensive = None
    if enable_summary and shared.models.offensive_query_classifier is not None:
        log_offensive_query_classifier_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.OFFENSIVE_QUERY_CLASSIFIER.value,
        )
        is_offensive = is_query_offensive(
            model=shared.models.offensive_query_classifier,
            query=query,
        )
        log_offensive_query_classifier_timing_event()

    return QueryFeatures(
        is_synthesizable=is_synthesizable,
        is_yes_no_question=is_yes_no_question,
        is_offensive=is_offensive,
    )
