from dataclasses import dataclass

import torch
from transformers.models.auto.modeling_auto import (  # type: ignore
    AutoModelForSequenceClassification,
)
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_OFFENSIVE_QUERY_MODEL = "Consensus/offensive_query_v0.1"

MODEL_VERSION_OFFENSIVE_QUERY = f"{_HUGGING_FACE_OFFENSIVE_QUERY_MODEL}"


@dataclass(frozen=True)
class OffensiveQueryClassifier:
    model: AutoModelForSequenceClassification
    tokenizer: AutoTokenizer


def initialize_offensive_query_classifier(hf_api_key: str) -> OffensiveQueryClassifier:
    """
    Returns a model and tokenizer to use with the offensive query classifier.
    """
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_OFFENSIVE_QUERY_MODEL,
        use_auth_token=hf_api_key,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_OFFENSIVE_QUERY_MODEL,
        use_auth_token=hf_api_key,
        num_labels=2,
    )
    return OffensiveQueryClassifier(model=model, tokenizer=tokenizer)


def is_query_offensive(
    model: OffensiveQueryClassifier,
    query: str,
) -> bool:
    """
    Returns true if the query is classified as offensive, false otherwise.
    """
    inputs = model.tokenizer(
        query, padding=True, truncation=True, max_length=20, return_tensors="pt"
    )
    output = model.model(**inputs)
    probs = torch.nn.functional.softmax(output["logits"], dim=1).detach().numpy().tolist()[0]

    is_offensive_query: bool = probs[1] < 0.5
    return is_offensive_query
