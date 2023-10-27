import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common.cache.redis_connection import RedisEnv
from common.config.secret_manager import SecretId, access_secret
from common.db.connect import DbEnv
from common.search.connect import SearchEnv
from common.storage.connect import StorageEnv

TITLE = "Consensus Chat GPT Plugin"
VERSION = "1.0"
PUBLIC_DIR = "web/chat_gpt_plugin/app/public"
DEPLOYED_URLS_TO_OPENAI_VERIFICATION_TOKENS = {
    "https://dev.chat.consensus.app": "a29cb0eb8e5646039dcf4fe2cd342503",
    "https://chat.consensus.app": "dedf0e6640604b0e962489b4bc30aaa4",
}


_MAX_DB_CONNECTIONS = 5


@dataclass(frozen=True)
class BackendConfig:
    # Whether the app was started in a local enviornment.
    is_local_env: bool
    # Full url including external port
    deployed_url: Optional[str]
    # DB environment to connect to.
    db_env: DbEnv
    # Max number of DB connections allowed at a single time
    db_max_connections: int
    # Search environment to connect to.
    search_env: SearchEnv
    # Storage environment to connect to.
    storage_env: StorageEnv
    # Redis cache environment to connect to.
    redis_env: RedisEnv
    # Search index ID to query.
    search_index_id: str
    # Hugging face API key for accessing internal hub
    hf_access_token: str
    # Internal key for validating auth requests from ChatGPT
    consensus_auth_key: str


class _Env(Enum):
    """
    All environment variables for the backend web app.
    Next ID: 9
    """

    # Required: Environment
    WEB_CHAT_GPT_PLUGIN_ENV = 1  # ("local"|"dev"|"prod")

    # Required: Port to open the server on
    WEB_CHAT_GPT_PLUGIN_PORT = 2

    # Required: URL for deployed plugin, added to ai-plugin.json
    WEB_CHAT_GPT_PLUGIN_DEPLOYED_URL = 8

    # Optional: Log level. Default "info".
    WEB_CHAT_GPT_PLUGIN_LOG_LEVEL = 3  # ("critical"|"error"|"warning"|"info"|"debug"|"trace")

    # Required: Search index ID to query.
    WEB_CHAT_GPT_PLUGIN_SEARCH_INDEX = 4

    # Optional: Override for storage instance. Default to WEB_CHAT_GPT_PLUGIN_ENV if unset.
    WEB_CHAT_GPT_PLUGIN_DB_ENV = 5  # ("local"|"dev"|"prod")

    # Optional: Override for search instance. Default to WEB_CHAT_GPT_PLUGIN_ENV if unset.
    WEB_CHAT_GPT_PLUGIN_SEARCH_ENV = 6  # ("local"|"dev"|"prod")

    # Optional: Override for storage instance. Default to WEB_CHAT_GPT_PLUGIN_ENV if unset.
    WEB_CHAT_GPT_PLUGIN_STORAGE_ENV = 7  # ("local"|"dev"|"prod")


def is_local_env() -> bool:
    return os.environ[_Env.WEB_CHAT_GPT_PLUGIN_ENV.name] == "local"


def _get_db_env() -> DbEnv:
    env = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_ENV.name]
    if _Env.WEB_CHAT_GPT_PLUGIN_DB_ENV.name in os.environ:
        env = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_DB_ENV.name]
    return DbEnv(env)


def _get_search_env() -> SearchEnv:
    env = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_ENV.name]
    if _Env.WEB_CHAT_GPT_PLUGIN_SEARCH_ENV.name in os.environ:
        env = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_SEARCH_ENV.name]
    return SearchEnv(env)


def _get_storage_env() -> StorageEnv:
    env = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_ENV.name]
    if _Env.WEB_CHAT_GPT_PLUGIN_STORAGE_ENV.name in os.environ:
        env = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_STORAGE_ENV.name]
    return StorageEnv(env)


def _get_hugging_face_access_token() -> str:
    return access_secret(
        SecretId.HUGGING_FACE_ACCESS_TOKEN,
        use_env_var=is_local_env(),
    )


def _get_consensus_api_key() -> str:
    return access_secret(
        SecretId.CONSENSUS_CHAT_GPT_PLUGIN_API_KEY,
        use_env_var=is_local_env(),
    )


def get_port() -> int:
    return int(os.environ[_Env.WEB_CHAT_GPT_PLUGIN_PORT.name])


def get_log_level() -> str:
    log_level = "debug" if is_local_env() else "warning"
    if _Env.WEB_CHAT_GPT_PLUGIN_LOG_LEVEL.name in os.environ:
        log_level = os.environ[_Env.WEB_CHAT_GPT_PLUGIN_LOG_LEVEL.name]
    valid = ["critical", "error", "warning", "info", "debug", "trace"]
    if log_level not in valid:
        raise ValueError(f"Bad value for log level: found {log_level} expected {valid}")
    return log_level


def generate_config() -> BackendConfig:
    return BackendConfig(
        is_local_env=is_local_env(),
        deployed_url=os.environ[_Env.WEB_CHAT_GPT_PLUGIN_DEPLOYED_URL.name],
        db_max_connections=_MAX_DB_CONNECTIONS,
        db_env=_get_db_env(),
        search_env=_get_search_env(),
        storage_env=_get_storage_env(),
        redis_env=RedisEnv(os.environ[_Env.WEB_CHAT_GPT_PLUGIN_ENV.name]),
        search_index_id=os.environ[_Env.WEB_CHAT_GPT_PLUGIN_SEARCH_INDEX.name],
        hf_access_token=_get_hugging_face_access_token(),
        consensus_auth_key=_get_consensus_api_key(),
    )
