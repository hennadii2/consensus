from dataclasses import dataclass

import torch
from claim_pb2 import Claim
from common.search.data import PaperResult
from transformers.models.auto.modeling_auto import AutoModelForSeq2SeqLM  # type: ignore
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_SEARCH_RANKER_MODEL = (
    "Consensus/search_ranker_monot5_distilled_small_v0.1"  # noqa: E501
)

MODEL_VERSION_SEARCH_RANKER = f"{_HUGGING_FACE_SEARCH_RANKER_MODEL}"


@dataclass(frozen=True)
class QuestionAnswerRanker:
    model: AutoModelForSeq2SeqLM
    tokenizer: AutoTokenizer


def initialize_question_answer_ranker(hf_api_key: str) -> QuestionAnswerRanker:
    """
    Returns a model and tokenizer to use with reorder_search_results.
    """
    model = AutoModelForSeq2SeqLM.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_SEARCH_RANKER_MODEL,
        use_auth_token=hf_api_key,
    )
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_SEARCH_RANKER_MODEL,
        padding_side="left",
        use_auth_token=hf_api_key,
    )
    return QuestionAnswerRanker(model=model, tokenizer=tokenizer)


@dataclass(frozen=True)
class QuestionAnswerRankerPrediction:
    claim: Claim
    relevancy: float


@dataclass(frozen=True)
class QuestionAnswerPaperRankerPrediction:
    paper: PaperResult
    relevance: float


def rank_search_results(
    ranker: QuestionAnswerRanker,
    results: list[Claim],
    query: str,
) -> list[QuestionAnswerRankerPrediction]:
    """
    Runs a reordering model across all given results for a single query and returns
    a sorted sequence of IDs based on the performance of each result
    """
    if len(results) == 0:
        return []

    answers = [claim.metadata.text for claim in results]

    # generate query + answer pair
    payload = [f"Question: {query} </s> Answer: {a} </s> Good Answer: " for a in answers]

    inputs = ranker.tokenizer(
        payload,
        truncation=True,
        max_length=128,
        padding="max_length",
        return_tensors="pt",
    )
    outputs = ranker.model.generate(
        **inputs,
        max_new_tokens=1,
        return_dict_in_generate=True,
        output_scores=True,
    )
    true_false_scores = [score[[1176, 6136]] for score in outputs["scores"][0]]
    assert len(true_false_scores) == len(results)

    claims_with_probs: list[tuple[Claim, float]] = []
    for i in range(len(true_false_scores)):
        probability = torch.nn.functional.softmax(true_false_scores[i]).numpy().tolist()[0]
        claims_with_probs.append((results[i], probability))

    sorted_claims_with_probs = sorted(
        claims_with_probs,
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        QuestionAnswerRankerPrediction(
            claim=value[0],
            relevancy=value[1],
        )
        for value in sorted_claims_with_probs
    ]


def rank_paper_search_results(
    ranker: QuestionAnswerRanker,
    results: list[PaperResult],
    query: str,
) -> list[QuestionAnswerPaperRankerPrediction]:
    """
    Runs a ranking model on results for a single query and returns the ranked list of results
    """
    if len(results) == 0:
        return []

    answers = [paper.display_text for paper in results]

    # generate query + answer pair
    payload = [f"Question: {query} </s> Answer: {a} </s> Good Answer: " for a in answers]

    inputs = ranker.tokenizer(
        payload,
        truncation=True,
        max_length=128,
        padding="max_length",
        return_tensors="pt",
    )
    outputs = ranker.model.generate(
        **inputs,
        max_new_tokens=1,
        return_dict_in_generate=True,
        output_scores=True,
    )
    true_false_scores = [score[[1176, 6136]] for score in outputs["scores"][0]]
    assert len(true_false_scores) == len(results)

    papers_with_probs: list[tuple[PaperResult, float]] = []
    for i in range(len(true_false_scores)):
        probability = torch.nn.functional.softmax(true_false_scores[i]).numpy().tolist()[0]
        papers_with_probs.append((results[i], probability))

    sorted_papers_with_probs = sorted(
        papers_with_probs,
        key=lambda item: item[1],
        reverse=True,
    )
    return [
        QuestionAnswerPaperRankerPrediction(
            paper=value[0],
            relevance=value[1],
        )
        for value in sorted_papers_with_probs
    ]
