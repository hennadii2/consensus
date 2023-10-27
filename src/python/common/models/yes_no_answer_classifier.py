from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, TypedDict

import torch
from transformers.models.auto.modeling_auto import AutoModelForSeq2SeqLM  # type: ignore
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_YES_NO_ANSWERS_MODEL = "Consensus/yes_no_answers_t5_v0.5"
_DEFAULT_MIN_THRESHOLD_YES_NO_ANSWER = 0.7
MODEL_VERSION_YES_NO_ANSWER = (
    f"{_HUGGING_FACE_YES_NO_ANSWERS_MODEL}:{_DEFAULT_MIN_THRESHOLD_YES_NO_ANSWER}"  # noqa: E501
)


@dataclass(frozen=True)
class YesNoAnswerClassifier:
    model: AutoModelForSeq2SeqLM
    tokenizer: AutoTokenizer


def initialize_yes_no_answer_classifier(hf_api_key: str) -> YesNoAnswerClassifier:
    """
    Returns a model and tokenizer to use with yes/no classifiers.
    """
    answers_model = AutoModelForSeq2SeqLM.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_YES_NO_ANSWERS_MODEL,
        use_auth_token=hf_api_key,
    )
    answers_tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_YES_NO_ANSWERS_MODEL,
        padding_side="left",
        use_auth_token=hf_api_key,
    )
    return YesNoAnswerClassifier(
        model=answers_model,
        tokenizer=answers_tokenizer,
    )


class YesNoAnswerInput(TypedDict):
    text: str
    id: str
    paper_id: str


class YesNoAnswerClass(IntEnum):
    NO = 0
    OTHER = 1
    POSSIBLY = 2
    YES = 3


class YesNoPrediction(TypedDict):
    answer: YesNoAnswerClass
    probability: float


def classify_results_as_yes_or_no_answers(
    classifier: YesNoAnswerClassifier,
    inputs: list[YesNoAnswerInput],
    query: str,
    min_probability_threshold: Optional[float] = None,
) -> list[YesNoPrediction]:
    """
    Returns predictions for whether each input text answers the question.
    """
    if len(inputs) == 0:
        return []

    answers = [data["text"] for data in inputs]

    prompt = "what is the answer to the question \n (a) yes (b) possibly (c) no (d) other: "
    payload = [f"question: {query} </s> answer: {answer} {prompt}" for answer in answers]

    model_inputs = classifier.tokenizer(
        payload, truncation=True, max_length=100, padding="max_length", return_tensors="pt"
    )
    outputs = classifier.model.generate(
        **model_inputs,
        min_new_tokens=1,
        max_new_tokens=3,
        return_dict_in_generate=True,
        output_scores=True,
    )

    # score tokens: [no, other, possibly, yes]
    scores = [score[[150, 119, 3673, 4273]] for score in outputs["scores"][0]]
    assert len(scores) == len(inputs)

    preds = [torch.argmax(tfs, dim=-1).numpy().tolist() for tfs in scores]
    probs = [torch.nn.functional.softmax(tfs).numpy().tolist() for tfs in scores]

    threshold = (
        _DEFAULT_MIN_THRESHOLD_YES_NO_ANSWER
        if min_probability_threshold is None
        else min_probability_threshold
    )
    return [
        YesNoPrediction(
            answer=YesNoAnswerClass(preds[i])
            if probs[i][preds[i]] >= threshold
            else YesNoAnswerClass.OTHER,
            probability=probs[i][preds[i]],
        )
        for i in range(len(inputs))
    ]
