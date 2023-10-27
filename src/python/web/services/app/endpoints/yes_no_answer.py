from common.logging.timing import time_endpoint_event
from common.models.yes_no_answer_classifier import classify_results_as_yes_or_no_answers
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.services.api import YesNoAnswerRequest, YesNoAnswerResponse
from web.services.app.state import SharedState

router = APIRouter()


@router.post("/yes_no_answer", response_model=YesNoAnswerResponse)
def yes_no_answer(request: Request, data: YesNoAnswerRequest):
    shared: SharedState = request.app.state.shared

    try:
        if shared.models.yes_no_answer_classifier is None:
            raise ValueError("Yes/No model is not initialized.")

        log_run_yes_no = time_endpoint_event(
            endpoint="services_yes_no_answer",
            event="run_model",
        )
        predictions = classify_results_as_yes_or_no_answers(
            classifier=shared.models.yes_no_answer_classifier,
            inputs=data.inputs,
            query=data.query,
            min_probability_threshold=data.min_probability_threshold,
        )
        log_run_yes_no(normalize_by=len(data.inputs))
        return YesNoAnswerResponse(predictions=predictions)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
