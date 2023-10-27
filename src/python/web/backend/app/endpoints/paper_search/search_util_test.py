from common.db.abstract_takeaways import AbstractTakeaway
from common.models.question_answer_ranker import QuestionAnswerPaperRankerPrediction
from common.search.data import PaperResult
from web.backend.app.endpoints.paper_search.search_util import (
    _apply_abstract_takeaways,
    _apply_extracted_answers,
)


def test_apply_extracted_answers() -> None:
    results = [
        PaperResult(hash_paper_id="hash_one", paper_id="one", display_text="one"),
        PaperResult(hash_paper_id="hash_two", paper_id="two", display_text="two"),
        PaperResult(hash_paper_id="hash_three", paper_id="three", display_text="three"),
        PaperResult(hash_paper_id="hash_four", paper_id="four", display_text="four"),
        PaperResult(hash_paper_id="hash_five", paper_id="five", display_text="five"),
    ]
    answers = {
        "one": ("extracted one", 0.1),
        "two": ("extracted two", 0.2),
        "three": ("extracted three", 0.3),
        "five": ("extracted five", 0.5),
    }
    assert _apply_extracted_answers(results, answers) == [
        QuestionAnswerPaperRankerPrediction(
            paper=PaperResult(
                hash_paper_id="hash_one", paper_id="one", display_text="extracted one"
            ),
            relevance=0.1,
        ),
        QuestionAnswerPaperRankerPrediction(
            paper=PaperResult(
                hash_paper_id="hash_two", paper_id="two", display_text="extracted two"
            ),
            relevance=0.2,
        ),
        QuestionAnswerPaperRankerPrediction(
            paper=PaperResult(
                hash_paper_id="hash_three", paper_id="three", display_text="extracted three"
            ),
            relevance=0.3,
        ),
        QuestionAnswerPaperRankerPrediction(
            paper=PaperResult(
                hash_paper_id="hash_five", paper_id="five", display_text="extracted five"
            ),
            relevance=0.5,
        ),
    ]


def test_apply_abstract_takeaways() -> None:
    results = [
        PaperResult(hash_paper_id="hash_one", paper_id="one", display_text="one"),
        PaperResult(hash_paper_id="hash_two", paper_id="two", display_text="two"),
        PaperResult(hash_paper_id="hash_three", paper_id="three", display_text="three"),
        PaperResult(hash_paper_id="hash_four", paper_id="four", display_text="four"),
        PaperResult(hash_paper_id="hash_five", paper_id="five", display_text="five"),
    ]
    takeaways = [
        AbstractTakeaway(row_id=1, paper_id="one", takeaway="1", is_valid_for_product=True),
        AbstractTakeaway(row_id=2, paper_id="two", takeaway="2", is_valid_for_product=False),
        AbstractTakeaway(row_id=3, paper_id="three", takeaway="3", is_valid_for_product=True),
        None,
        AbstractTakeaway(row_id=4, paper_id="five", takeaway="5", is_valid_for_product=True),
    ]
    assert _apply_abstract_takeaways(results, takeaways) == [
        PaperResult(hash_paper_id="hash_one", paper_id="one", display_text="1"),
        PaperResult(hash_paper_id="hash_three", paper_id="three", display_text="3"),
        PaperResult(hash_paper_id="hash_five", paper_id="five", display_text="5"),
    ]
