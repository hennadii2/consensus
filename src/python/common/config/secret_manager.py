from datetime import datetime, timedelta
from enum import Enum
from os import environ
from typing import Dict

from google.cloud import secretmanager
from loguru import logger


class SecretId(Enum):
    """
    All secrets expected to be available in the secrets manager.
    """

    GCLOUD_PROJECT_ID = "gcloud-project-id"
    ELASTIC_URI_LOCAL = "elastic-uri-local"
    ELASTIC_URI_DEV = "elastic-uri-DEV-230119"
    ELASTIC_URI_PROD_INGEST = ""

    ELASTIC_URI_STAGING = "elastic-uri-prod-230908-lexical"
    ELASTIC_CLOUD_ID_STAGING = "elastic-cloud-id-prod-230908-lexical"

    ELASTIC_URI_PROD = "elastic-uri-prod-230908-lexical"
    ELASTIC_CLOUD_ID_PROD = "elastic-cloud-id-prod-230908-lexical"

    ELASTIC_URI_PAPER_SEARCH = "elastic-uri-paper-search"
    ELASTIC_CLOUD_ID_PAPER_SEARCH = "elastic-cloud-id-paper-search"

    PINECONE_API_KEY = "pinecone-api-key"
    POSTGRES_URI_LOCAL = "postgres-uri-local"
    POSTGRES_URI_DEV = "postgres-uri-dev"
    POSTGRES_URI_STAGING = ""
    POSTGRES_URI_PROD_INGEST = ""
    POSTGRES_URI_PROD = "postgres-uri-prod-3"
    POSTGRES_JDBC_URI_LOCAL = "postgres-jdbc-uri-local"
    POSTGRES_JDBC_URI_DEV = "postgres-jdbc-uri-dev"
    POSTGRES_JDBC_URI_PROD = "postgres-jdbc-uri-prod"
    REDIS_CACHE_URI_LOCAL = "redis-cache-uri-local"
    REDIS_CACHE_URI_DEV = "redis-cache-uri-dev"
    REDIS_CACHE_URI_PROD = "redis-cache-uri-prod"
    HUGGING_FACE_API_KEY = "hugging-face-api-key"
    HUGGING_FACE_ACCESS_TOKEN = "hugging-face-access-token"
    OPENAI_API_KEY = "openai-api-key"
    BASETEN_API_KEY = "baseten-api-key"
    S2_API_KEY = "semantic-scholar-api-key"

    CLERK_JWT_VERIFICATION_KEY_LOCAL = "clerk-jwt-verification-key-local"
    CLERK_JWT_VERIFICATION_KEY_DEV = "clerk-jwt-verification-key-dev"
    CLERK_JWT_VERIFICATION_KEY_PROD = "clerk-jwt-verification-key-prod"

    CONSENSUS_TEST_API_KEY = "consensus-test-api-key"
    CONSENSUS_CHAT_GPT_PLUGIN_API_KEY = "consensus-chat-gpt-plugin-api-key"

    SLACK_DEVBOT_API_KEY = "slack-devbot-api-token"


# Cache secrets in memory to reduce call volume to GCP. Expire secrets after 10 minutes.
secret_cache: Dict[SecretId, str] = {}
secret_timestamp: Dict[SecretId, datetime] = {}
SECRET_EXPIRY_MINUTES = 10


def _get_gcloud_secret(project_id: str, secret_id: SecretId, version_id: str) -> str:
    """
    Returns a secret value stored in GCP Secrets Manager.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id.value}/versions/{version_id}"
    try:
        response = client.access_secret_version(name=name)
        return str(response.payload.data.decode("UTF-8"))
    except Exception as e:
        logger.error(f"Failed to get cloud secret for: {secret_id.name}")
        raise e


def _get_env_var_secret(secret_id: SecretId, allow_empty: bool = False) -> str:
    """
    Returns a secret value set in the local environment.
    """
    if allow_empty and secret_id.name not in environ:
        return ""
    return environ[secret_id.name]


def access_secret(secret_id: SecretId, version_id="latest", use_env_var=False) -> str:
    """
    Returns a secret value stored in our secret manager.

    If use_env_var=True, then secrets will be read from environment variables.
    Otherwise, they will be read from GCP secret manager.
    """

    # Check if the secret is in the cache and is less than 10 minutes old
    now = datetime.utcnow()
    if secret_id in secret_timestamp:
        if now - secret_timestamp[secret_id] < timedelta(minutes=SECRET_EXPIRY_MINUTES):
            return secret_cache[secret_id]

    if use_env_var:
        secret_cache[secret_id] = _get_env_var_secret(secret_id)
    else:
        gcloud_project_id = _get_env_var_secret(SecretId.GCLOUD_PROJECT_ID)
        secret_cache[secret_id] = _get_gcloud_secret(gcloud_project_id, secret_id, version_id)

    secret_timestamp[secret_id] = now  # Set the timestamp of the current fetch
    return secret_cache[secret_id]
