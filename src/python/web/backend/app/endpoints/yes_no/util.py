from common.models.yes_no_answer_classifier import (
    YesNoAnswerClass,
    YesNoAnswerInput,
    YesNoPrediction,
)
from loguru import logger
from web.backend.app.common.disputed import DisputedData
from web.backend.app.common.util import partition, rounded_percent
from web.backend.app.endpoints.yes_no.data import AnswerPercents, YesNoResponse

UNKNOWN_STRING = "UNKNOWN"
EMPTY_ANSWERS = AnswerPercents(YES=0, NO=0, POSSIBLY=0)


def create_yes_no_response(
    yes_no_inputs: list[YesNoAnswerInput],
    yes_no_predictions: list[YesNoPrediction],
    min_num_results_with_answers_threshold: int,
    disputed: DisputedData,
    max_percent_disputed_threshold: float,
) -> YesNoResponse:
    assert len(yes_no_inputs) == len(yes_no_predictions)
    result_and_answers = list(zip(yes_no_inputs, yes_no_predictions))
    result_and_answers, other_result_and_answers = partition(
        lambda x: x[1]["answer"] != YesNoAnswerClass.OTHER, result_and_answers
    )
    if len(result_and_answers) < min_num_results_with_answers_threshold:
        return YesNoResponse(
            resultsAnalyzedCount=0,
            yesNoAnswerPercents=EMPTY_ANSWERS,
            resultIdToYesNoAnswer={},
            isDisputed=False,
            isIncomplete=True,
            isSkipped=False,
        )

    # Initialize yes/no counts
    yes_no_counts: dict[str, int] = {}
    for answer in YesNoAnswerClass:
        if answer == YesNoAnswerClass.OTHER:
            continue
        yes_no_string = answer.name
        yes_no_counts[yes_no_string] = 0

    # Parse classifier answers into response data
    total_count = 0
    disputed_count = 0
    result_id_to_yes_no: dict[str, str] = {}
    for result_and_answer in result_and_answers:
        yes_no_string = result_and_answer[1]["answer"].name
        yes_no_counts[yes_no_string] = yes_no_counts[yes_no_string] + 1
        result_id_to_yes_no[result_and_answer[0]["id"]] = yes_no_string
        if result_and_answer[0]["paper_id"] in disputed.disputed_badges_by_paper_id:
            disputed_count += 1
        total_count += 1

    # Add "UNKNOWN" string to claim ids map (but do not include in percents)
    for result_and_answer in other_result_and_answers:
        result_id_to_yes_no[result_and_answer[0]["id"]] = UNKNOWN_STRING

    # Convert counts to percents
    yes_no_percents = AnswerPercents(
        YES=rounded_percent(yes_no_counts[YesNoAnswerClass.YES.name] / total_count),
        NO=rounded_percent(yes_no_counts[YesNoAnswerClass.NO.name] / total_count),
        POSSIBLY=rounded_percent(yes_no_counts[YesNoAnswerClass.POSSIBLY.name] / total_count),
    )

    is_disputed = False
    disputed_percent = disputed_count / total_count
    if disputed_percent >= max_percent_disputed_threshold:
        is_disputed = True
        logger.info(f"Yes/No Disputed: {disputed_count} / {total_count} = {disputed_percent}")

    return YesNoResponse(
        resultsAnalyzedCount=total_count,
        yesNoAnswerPercents=yes_no_percents,
        resultIdToYesNoAnswer=result_id_to_yes_no,
        isDisputed=is_disputed,
        isIncomplete=False,
        isSkipped=False,
    )
