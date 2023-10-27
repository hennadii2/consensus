from dataclasses import dataclass
from enum import IntEnum

import torch
from transformers.models.auto.modeling_auto import (  # type: ignore
    AutoModelForSequenceClassification,
)
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_QUERY_MODEL = "Consensus/query_classifier_v0.3"

MODEL_VERSION_QUERY_CLASSIFIER = f"{_HUGGING_FACE_QUERY_MODEL}"


@dataclass(frozen=True)
class QueryClassifier:
    model: AutoModelForSequenceClassification
    tokenizer: AutoTokenizer


def initialize_query_classifier(hf_api_key: str) -> QueryClassifier:
    """
    Returns a model and tokenizer to use with the question classifier.
    """
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_QUERY_MODEL,
        use_auth_token=hf_api_key,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_QUERY_MODEL,
        use_auth_token=hf_api_key,
        num_labels=8,
    )
    return QueryClassifier(model=model, tokenizer=tokenizer)


class QueryClass(IntEnum):
    COMMAND = 0
    DESCRIPTION = 1
    KEYWORD = 2
    METADATA = 3
    OTHER = 4
    PHRASE = 5
    QUESTION = 6
    STATEMENT = 7


@dataclass(frozen=True)
class QueryClassifierPrediction:
    prediction: QueryClass
    probability: float


def _predict_query_class(
    classifier: QueryClassifier,
    query: str,
) -> list[QueryClassifierPrediction]:
    # predict question
    inputs = classifier.tokenizer(
        query.lower(),
        padding=True,
        truncation=True,
        max_length=20,
        return_tensors="pt",
    )
    logits = classifier.model(**inputs).logits
    probs = torch.nn.functional.softmax(logits, dim=-1)
    return [
        QueryClassifierPrediction(
            prediction=QueryClass(i),
            probability=probs[:, i].tolist()[0],
        )
        for i in range(probs.size(dim=1))
    ]


def is_query_synthesizable(
    classifier: QueryClassifier,
    query: str,
    use_v2: bool,
) -> bool:
    """
    Returns true if the query is considered synthesizable, false otherwise.
    """
    synthesizable_types = [
        QueryClass.QUESTION,
        QueryClass.PHRASE,
    ]
    # In v2 paper search, we want to synthesize on additional query types
    if use_v2:
        synthesizable_types.append(QueryClass.STATEMENT)

    predictions = _predict_query_class(
        classifier=classifier,
        query=query,
    )
    prediction = max(predictions, key=lambda x: x.probability).prediction

    return prediction in synthesizable_types
