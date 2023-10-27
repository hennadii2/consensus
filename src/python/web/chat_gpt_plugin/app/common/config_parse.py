import json
from typing import Optional

from pydantic import BaseModel


class AiPluginJsonAuth(BaseModel):
    type: str
    authorization_type: Optional[str]
    verification_tokens: Optional[dict[str, str]]


class AiPluginJsonApi(BaseModel):
    type: str
    url: str


class AiPluginConfig(BaseModel):
    schema_version: str
    name_for_human: str
    name_for_model: str
    description_for_human: str
    description_for_model: str
    auth: AiPluginJsonAuth
    api: AiPluginJsonApi
    logo_url: str
    contact_email: str
    legal_info_url: str


def parse_ai_plugin_config(json_text: str) -> AiPluginConfig:
    """
    Returns the contents of ai plugin json parsed into a model.
    """
    data = json.loads(json_text)
    ai_plugin = AiPluginConfig(**data)
    return ai_plugin
