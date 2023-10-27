from dataclasses import dataclass

import torch
from transformers.models.auto.modeling_auto import (  # type: ignore
    AutoModelForSequenceClassification,
)
from transformers.models.auto.tokenization_auto import AutoTokenizer  # type: ignore

_HUGGING_FACE_YES_NO_QUESTION_MODEL = "Consensus/yes_no_question_v0.1"
MODEL_VERSION_YES_NO_QUESTION = f"{_HUGGING_FACE_YES_NO_QUESTION_MODEL}"  # noqa: E501


@dataclass(frozen=True)
class YesNoQuestionClassifier:
    model: AutoModelForSequenceClassification
    tokenizer: AutoTokenizer


def initialize_yes_no_question_classifier(hf_api_key: str) -> YesNoQuestionClassifier:
    """
    Returns a model and tokenizer to use with yes/no classifiers.
    """
    question_tokenizer = AutoTokenizer.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_YES_NO_QUESTION_MODEL,
        use_auth_token=hf_api_key,
    )
    question_model = AutoModelForSequenceClassification.from_pretrained(
        pretrained_model_name_or_path=_HUGGING_FACE_YES_NO_QUESTION_MODEL,
        use_auth_token=hf_api_key,
        num_labels=2,
    )
    return YesNoQuestionClassifier(
        model=question_model,
        tokenizer=question_tokenizer,
    )


def is_query_a_yes_no_question(
    classifier: YesNoQuestionClassifier,
    query: str,
) -> bool:
    """
    Returns true if the query is considered a yes/no question, false otherwise.
    If true, the query and its answers can be passed through the answers classifier.
    """
    # predict question
    model_inputs = classifier.tokenizer(
        query, padding=True, truncation=True, max_length=20, return_tensors="pt"
    )
    q_output = classifier.model(**model_inputs)
    q_probs = torch.nn.functional.softmax(q_output["logits"], dim=1).detach().numpy().tolist()[0]
    is_yes_no_question: bool = q_probs[1] >= 0.5
    return is_yes_no_question
