from dataclasses import dataclass

import torch
from transformers.models.auto.modeling_auto import (  # type: ignore
    AutoModelForSequenceClassification,
)
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_QUESTION_MODEL = "Consensus/search_question_v0.1"

MODEL_VERSION_QUESTION_CLASSIFIER = f"{_HUGGING_FACE_QUESTION_MODEL}"


@dataclass(frozen=True)
class QuestionClassifier:
    model: AutoModelForSequenceClassification
    tokenizer: AutoTokenizer


def initialize_question_classifier(hf_api_key: str) -> QuestionClassifier:
    """
    Returns a model and tokenizer to use with the question classifier.
    """
    tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_QUESTION_MODEL,
        use_auth_token=hf_api_key,
    )
    model = AutoModelForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_QUESTION_MODEL,
        use_auth_token=hf_api_key,
        num_labels=2,
    )
    return QuestionClassifier(model=model, tokenizer=tokenizer)


def is_query_a_question(
    model: QuestionClassifier,
    query: str,
) -> bool:
    """
    Returns true if the query is a question, false otherwise.
    """
    # predict question
    inputs = model.tokenizer(
        query.lower(), padding=True, truncation=True, max_length=20, return_tensors="pt"
    )
    q_output = model.model(**inputs)
    q_probs = torch.nn.functional.softmax(q_output["logits"], dim=1).detach().numpy().tolist()[0]
    is_question: bool = q_probs[1] >= 0.5
    return is_question
