import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common.config.secret_manager import SecretId, access_secret

TITLE = "Consensus Services"
VERSION = "1.0"


@dataclass(frozen=True)
class BackendConfig:
    # Whether the app was started in a local enviornment.
    is_local_env: bool
    # Hugging face API key for accessing internal hub
    hf_access_token: Optional[str]
    # Openai API key for internal models
    openai_api_key: Optional[str]
    # Whether or not to enable heavy models which may take a while to load
    enable_heavy_models: bool


class _Env(Enum):
    """
    All environment variables for the backend web app.
    Next ID: 5
    """

    # Required: Environment
    WEB_SERVICES_ENV = 1  # ("local"|"dev"|"prod")

    # Required: Port to open the server on
    WEB_SERVICES_PORT = 2

    # Optional: Log level. Default "info".
    WEB_SERVICES_LOG_LEVEL = 3  # ("critical"|"error"|"warning"|"info"|"debug"|"trace")

    # Optional: Default to false if unset.
    WEB_SERVICES_DISABLE_LARGE_MODELS = 4  # (true)


def is_local_env() -> bool:
    return os.environ[_Env.WEB_SERVICES_ENV.name] == "local"


def _get_hugging_face_access_token() -> Optional[str]:
    try:
        if is_local_env():
            return access_secret(SecretId.HUGGING_FACE_ACCESS_TOKEN, use_env_var=True)
        else:
            return access_secret(SecretId.HUGGING_FACE_ACCESS_TOKEN)
    except Exception:
        return None


def _get_openai_api_key() -> Optional[str]:
    try:
        if is_local_env():
            return access_secret(SecretId.OPENAI_API_KEY, use_env_var=True)
        else:
            return access_secret(SecretId.OPENAI_API_KEY)
    except Exception:
        return None


def get_port() -> int:
    return int(os.environ[_Env.WEB_SERVICES_PORT.name])


def get_log_level() -> str:
    log_level = "debug" if is_local_env() else "warning"
    if _Env.WEB_SERVICES_LOG_LEVEL.name in os.environ:
        log_level = os.environ[_Env.WEB_SERVICES_LOG_LEVEL.name]
    valid = ["critical", "error", "warning", "info", "debug", "trace"]
    if log_level not in valid:
        raise ValueError(f"Bad value for log level: found {log_level} expected {valid}")
    return log_level


def generate_config() -> BackendConfig:
    return BackendConfig(
        is_local_env=is_local_env(),
        hf_access_token=_get_hugging_face_access_token(),
        openai_api_key=_get_openai_api_key(),
        enable_heavy_models=(
            not bool(os.environ.get(_Env.WEB_SERVICES_DISABLE_LARGE_MODELS.name, False))
        ),
    )
