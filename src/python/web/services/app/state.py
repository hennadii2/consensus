from dataclasses import dataclass
from typing import Optional

from common.models.yes_no_answer_classifier import (
    YesNoAnswerClassifier,
    initialize_yes_no_answer_classifier,
)
from loguru import logger
from web.services.app.config import BackendConfig


@dataclass(frozen=True)
class Models:
    yes_no_answer_classifier: Optional[YesNoAnswerClassifier]


@dataclass(frozen=True)
class SharedState:
    models: Models


def initialize_models(
    hf_access_token: Optional[str],
    enable_heavy_models: bool,
) -> Models:
    return Models(
        yes_no_answer_classifier=(
            initialize_yes_no_answer_classifier(hf_api_key=hf_access_token)
            if hf_access_token is not None and enable_heavy_models
            else None
        ),
    )


def initialize_shared_state(config: BackendConfig) -> SharedState:
    shared = SharedState(
        models=initialize_models(
            hf_access_token=config.hf_access_token,
            enable_heavy_models=config.enable_heavy_models,
        ),
    )
    logger.info(f"Enabled yes/no answer: {shared.models.yes_no_answer_classifier is not None}")

    return shared
