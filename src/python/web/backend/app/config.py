import os
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from common.cache.redis_connection import RedisEnv
from common.config.secret_manager import SecretId, access_secret
from common.db.connect import DbEnv
from common.search.connect import SearchEnv
from common.storage.connect import StorageEnv
from web.backend.app.common.auth import AuthEnv

TITLE = "Consensus App"
VERSION = "1.0"
_MAX_DB_CONNECTIONS = 5
_OBFUSCATION_KEY_NOT_FOR_SECURE_DATA = "ZR3a2OF3zMoz4_8-XN-cUVkdQsfUDjLCpLNVVASKvV8="


@dataclass(frozen=True)
class BackendConfig:
    # Whether the app was started in a local enviornment.
    is_local_env: bool
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
    # Clerk auth environment to connect validate against.
    auth_env: AuthEnv
    # Search index ID to query.
    search_index_id: str
    # Paper search index ID to query.
    paper_search_index_id: str
    # [TEMPORARY] Paper search index ID to query on the claim cluster.
    # This is used to isolate V2 infrastructure while we are still on claim search.
    paper_search_index_id_on_claim_cluster: Optional[str]
    # Autocomplete search index ID to query.
    autocomplete_index_id: Optional[str]
    # Hugging face API key for accessing internal hub
    hf_access_token: Optional[str]
    # Openai API key for internal models
    openai_api_key: Optional[str]
    # Baseten API key for internal models
    baseten_api_key: Optional[str]
    # Whether or not to enable heavy models not suitable for dev
    enable_heavy_models: bool
    # Encryption key used to avoid sending plain text data (eg. cache key) to client
    obfuscation_encrypt_key: str
    # Hostname for the services backend
    services_host: str
    # If true v2 paper records table is used to read papers
    use_papers_v2: bool


class _Env(Enum):
    """
    All environment variables for the backend web app.
    Next ID: 11
    """

    # Required: Environment
    WEB_BACKEND_ENV = 1  # ("local"|"dev"|"prod")

    # Required: Port to open the server on
    WEB_BACKEND_PORT = 5

    # Required: Search index ID to query.
    WEB_BACKEND_SEARCH_INDEX = 6

    # Optional: Autocomplete index ID to query.
    WEB_BACKEND_AUTOCOMPLETE_INDEX = 8

    # Optional: Log level. Default "info".
    WEB_BACKEND_LOG_LEVEL = 2  # ("critical"|"error"|"warning"|"info"|"debug"|"trace")

    # Optional: Override for DB instance. Default to WEB_BACKEND_ENV if unset.
    WEB_BACKEND_DB_ENV = 3  # ("local"|"dev"|"prod")

    # Optional: Override for search instance. Default to WEB_BACKEND_ENV if unset.
    WEB_BACKEND_SEARCH_ENV = 4  # ("local"|"dev"|"prod")

    # Optional: Override for storage instance. Default to WEB_BACKEND_ENV if unset.
    WEB_BACKEND_STORAGE_ENV = 7  # ("local"|"dev"|"prod")

    # Optional: Default to false if unset.
    WEB_BACKEND_DISABLE_LARGE_MODELS = 9  # (true)

    # Required: Web services host.
    WEB_BACKEND_SERVICES_HOST = 10


def is_local_env() -> bool:
    return os.environ[_Env.WEB_BACKEND_ENV.name] == "local"


def _get_db_env() -> DbEnv:
    env = os.environ[_Env.WEB_BACKEND_ENV.name]
    if _Env.WEB_BACKEND_DB_ENV.name in os.environ:
        env = os.environ[_Env.WEB_BACKEND_DB_ENV.name]
    return DbEnv(env)


def _get_search_env() -> SearchEnv:
    env = os.environ[_Env.WEB_BACKEND_ENV.name]
    if _Env.WEB_BACKEND_SEARCH_ENV.name in os.environ:
        env = os.environ[_Env.WEB_BACKEND_SEARCH_ENV.name]
    return SearchEnv(env)


def _get_storage_env() -> StorageEnv:
    env = os.environ[_Env.WEB_BACKEND_ENV.name]
    if _Env.WEB_BACKEND_STORAGE_ENV.name in os.environ:
        env = os.environ[_Env.WEB_BACKEND_STORAGE_ENV.name]
    return StorageEnv(env)


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


def _get_baseten_api_key() -> Optional[str]:
    try:
        if is_local_env():
            return access_secret(SecretId.BASETEN_API_KEY, use_env_var=True)
        else:
            return access_secret(SecretId.BASETEN_API_KEY)
    except Exception:
        return None


def _get_autocomplete_index_id() -> Optional[str]:
    if _Env.WEB_BACKEND_AUTOCOMPLETE_INDEX.name in os.environ:
        return os.environ[_Env.WEB_BACKEND_AUTOCOMPLETE_INDEX.name]
    return None


def _get_paper_search_index_id() -> str:
    # TODO(meganvw): Hard coding values until switch to v2
    if is_local_env():
        return f"{os.environ[_Env.WEB_BACKEND_SEARCH_INDEX.name]}-paper-search"
    else:
        return "paper-index-231024173343"


def _get_paper_search_index_id_on_claim_cluster() -> Optional[str]:
    # TODO(meganvw): This should be removed on v2 launch
    search_env = _get_search_env()
    if search_env != SearchEnv.PROD:
        return None
    return "paper-index-trimmed-231024064353"


def get_port() -> int:
    return int(os.environ[_Env.WEB_BACKEND_PORT.name])


def get_log_level() -> str:
    log_level = "debug" if is_local_env() else "warning"
    if _Env.WEB_BACKEND_LOG_LEVEL.name in os.environ:
        log_level = os.environ[_Env.WEB_BACKEND_LOG_LEVEL.name]
    valid = ["critical", "error", "warning", "info", "debug", "trace"]
    if log_level not in valid:
        raise ValueError(f"Bad value for log level: found {log_level} expected {valid}")
    return log_level


def generate_config() -> BackendConfig:
    search_env = _get_search_env()
    db_env = _get_db_env()
    return BackendConfig(
        is_local_env=is_local_env(),
        db_env=db_env,
        db_max_connections=_MAX_DB_CONNECTIONS,
        search_env=search_env,
        storage_env=_get_storage_env(),
        redis_env=RedisEnv(os.environ[_Env.WEB_BACKEND_ENV.name]),
        auth_env=AuthEnv(os.environ[_Env.WEB_BACKEND_ENV.name]),
        search_index_id=os.environ[_Env.WEB_BACKEND_SEARCH_INDEX.name],
        paper_search_index_id=_get_paper_search_index_id(),
        paper_search_index_id_on_claim_cluster=_get_paper_search_index_id_on_claim_cluster(),
        services_host=os.environ[_Env.WEB_BACKEND_SERVICES_HOST.name],
        autocomplete_index_id=_get_autocomplete_index_id(),
        enable_heavy_models=(
            not bool(os.environ.get(_Env.WEB_BACKEND_DISABLE_LARGE_MODELS.name, False))
        ),
        hf_access_token=_get_hugging_face_access_token(),
        openai_api_key=_get_openai_api_key(),
        baseten_api_key=_get_baseten_api_key(),
        obfuscation_encrypt_key=_OBFUSCATION_KEY_NOT_FOR_SECURE_DATA,
        use_papers_v2=True,
    )
