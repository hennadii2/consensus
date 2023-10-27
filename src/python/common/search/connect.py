from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple
from urllib.parse import urlparse

from common.config.secret_manager import SecretId, access_secret
from elasticsearch import AsyncElasticsearch, Elasticsearch
from loguru import logger

MAX_TIMEOUT_SECONDS = 30
MAX_RETRIES_COUNT = 10


class SearchEnv(Enum):
    """
    All supported search instance environments.
    """

    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"
    PROD_INGEST = "prod-ingest"
    LOCAL = "local"
    PAPER_SEARCH = "paper-search"


@dataclass
class SearchConnectionInfo:
    host: Optional[str]
    port: Optional[int]
    user: Optional[str]
    password: Optional[str]
    use_api_key: bool
    cloud_id: Optional[str]


def get_connection_info(env: SearchEnv) -> SearchConnectionInfo:
    """
    Returns a dataclass with parsed elastic search connection fields for the
    environment or throws an error.

    Raises:
        ValueError: if environment is not supported
    """

    def get_uri() -> Tuple[str, bool, Optional[str]]:
        if env == SearchEnv.LOCAL:
            uri = access_secret(SecretId.ELASTIC_URI_LOCAL, use_env_var=True)
            return (uri, False, None)
        elif env == SearchEnv.DEV:
            uri = access_secret(SecretId.ELASTIC_URI_DEV)
            return (uri, True, None)
        elif env == SearchEnv.STAGING:
            uri = access_secret(SecretId.ELASTIC_URI_STAGING)
            cloud_id = access_secret(SecretId.ELASTIC_CLOUD_ID_STAGING)
            return (uri, True, cloud_id)
        elif env == SearchEnv.PROD_INGEST:
            uri = access_secret(SecretId.ELASTIC_URI_PROD_INGEST)
            prod_uri = access_secret(SecretId.ELASTIC_URI_PROD)
            if uri == prod_uri:
                raise ValueError(
                    """
                PROD_INGEST environment cannot be the same value as PROD environment.
                Please verify that you are ingesting into a 2nd elasticsearch instance
                which is not actively used by production.
                """
                )
            return (uri, True, None)
        elif env == SearchEnv.PROD:
            uri = access_secret(SecretId.ELASTIC_URI_PROD)
            cloud_id = access_secret(SecretId.ELASTIC_CLOUD_ID_PROD)
            return (uri, True, cloud_id)
        elif env == SearchEnv.PAPER_SEARCH:
            uri = access_secret(SecretId.ELASTIC_URI_PAPER_SEARCH)
            cloud_id = access_secret(SecretId.ELASTIC_CLOUD_ID_PAPER_SEARCH)
            return (uri, True, cloud_id)
        else:
            raise ValueError(f"Failed to get search connection URI: unknown env {env}")

    connection_uri, use_api_key, cloud_id = get_uri()
    parsed_connection_uri = urlparse(connection_uri)
    return SearchConnectionInfo(
        host=parsed_connection_uri.hostname,
        port=parsed_connection_uri.port,
        user=parsed_connection_uri.username,
        password=parsed_connection_uri.password,
        use_api_key=use_api_key,
        cloud_id=cloud_id,
    )


def ElasticClient(env: SearchEnv) -> Elasticsearch:
    """
    Connects to an elasticsearch cluster.

    Raises:
        ValueError: if elasticsearch config is not available
        ConnectionError: if elasticsearch client is not reachable
    """

    info = get_connection_info(env)

    config_error = "Failed to connect to search for env {0}: {1}"
    if not info.host:
        raise ValueError(config_error.format(env, "host is none"))
    if not info.port:
        raise ValueError(config_error.format(env, "port is none"))
    if not info.user:
        raise ValueError(config_error.format(env, "user is none"))
    if not info.password:
        raise ValueError(config_error.format(env, "password is none"))

    logger.info(f"Connecting to {env.value} search: {info.host} {info.port} {info.user}")
    es = None
    if info.use_api_key:
        es = Elasticsearch(
            hosts=None
            if info.cloud_id is not None
            else [
                {
                    "host": info.host,
                    "port": info.port,
                    "use_ssl": True,
                }
            ],
            api_key=info.password,
            cloud_id=info.cloud_id,
            request_timeout=MAX_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES_COUNT,
            retry_on_timeout=True,
        )
    else:
        es = Elasticsearch(
            hosts=None
            if info.cloud_id is not None
            else [
                {
                    "host": info.host,
                    "port": info.port,
                    "use_ssl": False,
                }
            ],
            http_auth=(info.user, info.password),
            cloud_id=info.cloud_id,
            request_timeout=MAX_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES_COUNT,
            retry_on_timeout=True,
        )

    return es


def AsyncElasticClient(env: SearchEnv) -> AsyncElasticsearch:
    """
    Connects to an elasticsearch cluster.

    Raises:
        ValueError: if elasticsearch config is not available
        ConnectionError: if elasticsearch client is not reachable
    """

    info = get_connection_info(env)

    config_error = "Failed to connect to search for env {0}: {1}"
    if not info.host:
        raise ValueError(config_error.format(env, "host is none"))
    if not info.port:
        raise ValueError(config_error.format(env, "port is none"))
    if not info.user:
        raise ValueError(config_error.format(env, "user is none"))
    if not info.password:
        raise ValueError(config_error.format(env, "password is none"))

    logger.info(f"Connecting to {env.value} search: {info.host} {info.port} {info.user}")
    es = None
    if info.use_api_key:
        es = AsyncElasticsearch(
            hosts=None
            if info.cloud_id is not None
            else [
                {
                    "host": info.host,
                    "port": info.port,
                    "use_ssl": True,
                }
            ],
            api_key=info.password,
            cloud_id=info.cloud_id,
            request_timeout=MAX_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES_COUNT,
            retry_on_timeout=True,
        )
    else:
        es = AsyncElasticsearch(
            hosts=None
            if info.cloud_id is not None
            else [
                {
                    "host": info.host,
                    "port": info.port,
                    "use_ssl": False,
                }
            ],
            http_auth=(info.user, info.password),
            cloud_id=info.cloud_id,
            request_timeout=MAX_TIMEOUT_SECONDS,
            max_retries=MAX_RETRIES_COUNT,
            retry_on_timeout=True,
        )

    return es
