from contextlib import contextmanager
from typing import Generator, Optional

from common.cache.redis_connection import RedisEnv
from common.db.connect import DbEnv
from common.db.db_connection_handler import DbConnectionHandler
from common.db.test.connect import MainDbPoolTestClient
from common.models.similarity_search_embedding import initialize_similarity_search_embedding_model
from common.search.connect import SearchEnv
from common.storage.connect import StorageEnv, init_storage_client
from elasticsearch import AsyncElasticsearch, Elasticsearch
from fastapi.testclient import TestClient
from testcontainers.elasticsearch import ElasticSearchContainer  # type: ignore
from web.backend.app.common.auth import AuthEnv
from web.backend.app.common.test.redis_connection import RedisTestConnection
from web.backend.app.config import BackendConfig
from web.backend.app.main import app
from web.backend.app.state import Models, SharedState

_TEST_SEARCH_INDEX_ID = "test-search-index"
_TEST_AUTOCOMPLETE_INDEX_ID = "test-autocomplete-index"
_TEST_OBFUSCATION_ENCYRPT_KEY = "test-obfuscation-encrypt-key"
_TEST_MAX_DB_CONNECTIONS = 1


def init_test_config(
    hf_access_token: Optional[str] = None,
    openai_api_key: Optional[str] = None,
    baseten_api_key: Optional[str] = None,
) -> BackendConfig:
    return BackendConfig(
        is_local_env=True,
        services_host="services_host",
        db_env=DbEnv.LOCAL,
        db_max_connections=_TEST_MAX_DB_CONNECTIONS,
        search_env=SearchEnv.LOCAL,
        storage_env=StorageEnv.LOCAL,
        redis_env=RedisEnv.LOCAL,
        auth_env=AuthEnv.LOCAL,
        search_index_id=_TEST_SEARCH_INDEX_ID,
        paper_search_index_id=_TEST_SEARCH_INDEX_ID,
        paper_search_index_id_on_claim_cluster=None,
        autocomplete_index_id=_TEST_AUTOCOMPLETE_INDEX_ID,
        enable_heavy_models=hf_access_token is not None,
        hf_access_token=hf_access_token,
        openai_api_key=openai_api_key,
        baseten_api_key=baseten_api_key,
        obfuscation_encrypt_key=_TEST_OBFUSCATION_ENCYRPT_KEY,
        use_papers_v2=False,
    )


@contextmanager
def AppTestClient(config: BackendConfig) -> Generator[TestClient, None, None]:
    with ElasticSearchContainer("elasticsearch:8.6.0") as container:
        with RedisTestConnection() as redis:
            with MainDbPoolTestClient(max_connections=config.db_max_connections) as db:
                es = Elasticsearch(hosts=[container.get_url()])
                async_es = AsyncElasticsearch(hosts=[container.get_url()])

                app.state.shared = SharedState(
                    config=config,
                    services=None,
                    db=DbConnectionHandler(db),
                    es=es,
                    async_es=async_es,
                    paper_search_async_es=None,
                    storage_client=init_storage_client(config.storage_env),
                    redis=redis,
                    models=Models(
                        embedding_model=initialize_similarity_search_embedding_model(),
                        question_answer_ranker=None,
                        yes_no_question_classifier=None,
                        query_classifier=None,
                        offensive_query_classifier=None,
                        is_openai_initialized=False,
                        answer_extractor=None,
                    ),
                )
                client = TestClient(app)
                yield client
