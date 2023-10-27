from dataclasses import dataclass
from enum import IntEnum
from typing import Optional, TypedDict

import torch
from transformers.models.auto.modeling_auto import (  # type: ignore
    AutoModelForSequenceClassification,
)
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_STUDY_TYPE_MODEL = "Consensus/study_type_v1.0"
_DEFAULT_MIN_THRESHOLD = 0.75

MODEL_VERSION_STUDY_TYPE = f"{_HUGGING_FACE_STUDY_TYPE_MODEL}:{_DEFAULT_MIN_THRESHOLD}"


def study_type_or_none_if_below_threshold(
    study_type: Optional[str], probability: Optional[float]
) -> Optional[str]:
    if study_type is None or probability is None or probability < _DEFAULT_MIN_THRESHOLD:
        return None
    return study_type


@dataclass(frozen=True)
class StudyTypeClassifier:
    model: AutoModelForSequenceClassification
    tokenizer: AutoTokenizer


def initialize_study_type_classifier(hf_api_key: str) -> StudyTypeClassifier:
    """
    Returns a model and tokenizer to use with study type functions.
    """
    question_tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_STUDY_TYPE_MODEL,
        use_auth_token=hf_api_key,
    )
    question_model = AutoModelForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_STUDY_TYPE_MODEL,
        use_auth_token=hf_api_key,
        num_labels=6,
    )
    return StudyTypeClassifier(
        model=question_model,
        tokenizer=question_tokenizer,
    )


class StudyTypeClass(IntEnum):
    CASE_REPORT = 0
    META_ANALYSIS = 1
    NON_RCT_STUDY = 2
    OTHER = 3
    RCT_STUDY = 4
    SYSTEMATIC_REVIEW = 5


class StudyTypePrediction(TypedDict):
    value: StudyTypeClass
    probability: float


class StudyTypeInput(TypedDict):
    title: str
    abstract: str


def predict_study_types(
    classifier: StudyTypeClassifier,
    inputs: list[StudyTypeInput],
    min_probability_threshold: Optional[float] = None,
) -> list[StudyTypePrediction]:
    """
    Returns study type classifications for multiple title and abstract.
    """

    if len(inputs) == 0:
        return []

    payload = [f"Title: {x['title']} </s> Abstract: {x['abstract']}" for x in inputs]
    model_inputs = classifier.tokenizer(
        payload, padding=True, truncation=True, max_length=512, return_tensors="pt"
    )
    logits = classifier.model(**model_inputs).logits
    preds = torch.argmax(logits, dim=1).numpy().tolist()
    probs = torch.nn.functional.softmax(logits, dim=1).detach().numpy().tolist()

    predictions = []
    for i in range(len(preds)):
        prediction = preds[i]
        probability = probs[i][prediction]
        threshold = (
            _DEFAULT_MIN_THRESHOLD
            if min_probability_threshold is None
            else min_probability_threshold
        )
        predictions.append(
            StudyTypePrediction(
                value=StudyTypeClass(prediction)
                if probability >= threshold
                else StudyTypeClass.OTHER,
                probability=probability,
            )
        )
    return predictions


def predict_study_type(
    classifier: StudyTypeClassifier,
    input: StudyTypeInput,
    min_probability_threshold: Optional[float] = None,
) -> StudyTypePrediction:
    """
    Returns study type classification for a title and abstract.
    """

    payload = f"Title: {input['title']} </s> Abstract: {input['abstract']}"
    model_inputs = classifier.tokenizer(
        payload, padding=True, truncation=True, max_length=512, return_tensors="pt"
    )

    logits = classifier.model(**model_inputs).logits

    preds = torch.argmax(logits, dim=1).numpy().tolist()
    probs = torch.nn.functional.softmax(logits, dim=1).detach().numpy().tolist()
    prediction = preds[0]
    probability = probs[0][prediction]

    threshold = (
        _DEFAULT_MIN_THRESHOLD if min_probability_threshold is None else min_probability_threshold
    )

    return StudyTypePrediction(
        value=StudyTypeClass(prediction) if probability >= threshold else StudyTypeClass.OTHER,
        probability=probability,
    )
