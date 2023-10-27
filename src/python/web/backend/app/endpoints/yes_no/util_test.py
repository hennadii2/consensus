import web.backend.app.endpoints.yes_no.util as util
from common.models.yes_no_answer_classifier import (
    YesNoAnswerClass,
    YesNoAnswerInput,
    YesNoPrediction,
)
from web.backend.app.common.badges import DisputedBadge
from web.backend.app.common.disputed import DisputedData
from web.backend.app.endpoints.yes_no.data import AnswerPercents, YesNoResponse


def mock_yes_no_prediction(
    claim_id: str,
    paper_id: str = "1",
    answer: YesNoAnswerClass = YesNoAnswerClass.YES,
    probability: float = 0.5,
) -> tuple[YesNoAnswerInput, YesNoPrediction]:
    claim: YesNoAnswerInput = {"text": "mock-text", "id": claim_id, "paper_id": paper_id}
    return (
        claim,
        YesNoPrediction(
            answer=answer,
            probability=probability,
        ),
    )


def test_create_yes_no_response_incomplete_if_not_enough_claims() -> None:
    mock_claims_and_answers = [
        mock_yes_no_prediction(claim_id="1"),
        mock_yes_no_prediction(claim_id="2"),
    ]
    yes_no_inputs = [x[0] for x in mock_claims_and_answers]
    yes_no_predictions = [x[1] for x in mock_claims_and_answers]
    mock_disputed = DisputedData(
        version="mock",
        disputed_badges_by_paper_id={},
        known_background_claim_ids={},
    )

    # Above threshold
    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=0,
        disputed=mock_disputed,
        max_percent_disputed_threshold=1.0,
    )
    expected = YesNoResponse(
        resultsAnalyzedCount=2,
        yesNoAnswerPercents=AnswerPercents(YES=100, NO=0, POSSIBLY=0),
        resultIdToYesNoAnswer={"1": "YES", "2": "YES"},
        isDisputed=False,
        isIncomplete=False,
        isSkipped=False,
    )
    assert actual == expected

    # At threshold
    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=2,
        disputed=mock_disputed,
        max_percent_disputed_threshold=1.0,
    )
    expected = YesNoResponse(
        resultsAnalyzedCount=2,
        yesNoAnswerPercents=AnswerPercents(YES=100, NO=0, POSSIBLY=0),
        resultIdToYesNoAnswer={"1": "YES", "2": "YES"},
        isDisputed=False,
        isIncomplete=False,
        isSkipped=False,
    )
    assert actual == expected

    # Below threshold
    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=10,
        disputed=mock_disputed,
        max_percent_disputed_threshold=1.0,
    )
    expected = YesNoResponse(
        resultsAnalyzedCount=0,
        yesNoAnswerPercents=AnswerPercents(YES=0, NO=0, POSSIBLY=0),
        resultIdToYesNoAnswer={},
        isDisputed=False,
        isIncomplete=True,
        isSkipped=False,
    )
    assert actual == expected


def test_create_yes_no_response_disputed_if_too_many_disputed_claims() -> None:
    mock_claims_and_answers = [
        mock_yes_no_prediction(claim_id="1", paper_id="1"),
        mock_yes_no_prediction(claim_id="2", paper_id="2"),
    ]
    yes_no_inputs = [x[0] for x in mock_claims_and_answers]
    yes_no_predictions = [x[1] for x in mock_claims_and_answers]
    mock_disputed = DisputedData(
        version="mock",
        disputed_badges_by_paper_id={"1": DisputedBadge(reason="test", url="test")},
        known_background_claim_ids={},
    )
    expected = YesNoResponse(
        resultsAnalyzedCount=2,
        yesNoAnswerPercents=AnswerPercents(YES=100, NO=0, POSSIBLY=0),
        resultIdToYesNoAnswer={"1": "YES", "2": "YES"},
        isDisputed=False,
        isIncomplete=False,
        isSkipped=False,
    )

    # Below threshold
    threshold = 1.0
    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=0,
        disputed=mock_disputed,
        max_percent_disputed_threshold=threshold,
    )
    expected.isDisputed = False
    assert actual == expected

    # At threshold
    threshold = 0.5
    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=0,
        disputed=mock_disputed,
        max_percent_disputed_threshold=threshold,
    )
    expected.isDisputed = True
    assert actual == expected

    # Above threshold
    threshold = 0
    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=0,
        disputed=mock_disputed,
        max_percent_disputed_threshold=threshold,
    )
    expected.isDisputed = True
    assert actual == expected


def test_create_yes_no_response_adds_unknown_string_for_other_answer_but_skips_count() -> None:
    mock_claims_and_answers = [
        mock_yes_no_prediction(claim_id="1", paper_id="1", answer=YesNoAnswerClass.YES),
        mock_yes_no_prediction(claim_id="2", paper_id="2", answer=YesNoAnswerClass.NO),
        mock_yes_no_prediction(claim_id="3", paper_id="3", answer=YesNoAnswerClass.POSSIBLY),
        mock_yes_no_prediction(claim_id="4", paper_id="4", answer=YesNoAnswerClass.OTHER),
    ]
    yes_no_inputs = [x[0] for x in mock_claims_and_answers]
    yes_no_predictions = [x[1] for x in mock_claims_and_answers]
    mock_disputed = DisputedData(
        version="mock",
        disputed_badges_by_paper_id={},
        known_background_claim_ids={},
    )

    actual = util.create_yes_no_response(
        yes_no_inputs=yes_no_inputs,
        yes_no_predictions=yes_no_predictions,
        min_num_results_with_answers_threshold=0,
        disputed=mock_disputed,
        max_percent_disputed_threshold=1.0,
    )
    expected = YesNoResponse(
        resultsAnalyzedCount=3,
        yesNoAnswerPercents=AnswerPercents(YES=33, NO=33, POSSIBLY=33),
        resultIdToYesNoAnswer={"1": "YES", "2": "NO", "3": "POSSIBLY", "4": "UNKNOWN"},
        isDisputed=False,
        isIncomplete=False,
        isSkipped=False,
    )
    assert actual == expected
