from dataclasses import dataclass

import redis
from common.cache.redis_connection import RedisConnection
from common.db.connect import MainDbClientPool
from common.db.db_connection_handler import DbConnectionHandler
from common.models.question_answer_ranker import (
    QuestionAnswerRanker,
    initialize_question_answer_ranker,
)
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    initialize_similarity_search_embedding_model,
)
from common.search.connect import AsyncElasticClient
from common.storage.connect import StorageClient, init_storage_client
from elasticsearch import AsyncElasticsearch
from nltk import download as nltk_download
from web.chat_gpt_plugin.app.config import BackendConfig


@dataclass(frozen=True)
class Models:
    embedding_model: SimilaritySearchEmbeddingModel
    question_answer_ranker: QuestionAnswerRanker


@dataclass(frozen=True)
class SharedState:
    config: BackendConfig
    models: Models
    db: DbConnectionHandler
    async_es: AsyncElasticsearch
    storage_client: StorageClient
    redis: redis.Redis


def initialize_models(
    hf_access_token: str,
) -> Models:
    return Models(
        embedding_model=initialize_similarity_search_embedding_model(),
        question_answer_ranker=initialize_question_answer_ranker(hf_access_token),
    )


def initialize_shared_state(config: BackendConfig) -> SharedState:
    # Download required NLTK datasets
    nltk_download("stopwords")
    nltk_download("punkt")

    async_es = AsyncElasticClient(config.search_env)
    db_connection_handler = DbConnectionHandler(
        MainDbClientPool(
            env=config.db_env,
            max_connections=config.db_max_connections,
        )
    )
    shared = SharedState(
        config=config,
        models=initialize_models(
            hf_access_token=config.hf_access_token,
        ),
        db=db_connection_handler,
        async_es=async_es,
        storage_client=init_storage_client(config.storage_env),
        redis=RedisConnection(config.redis_env),
    )
    return shared
