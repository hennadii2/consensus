import os
from dataclasses import dataclass
from typing import Optional

import redis
from common.cache.redis_connection import RedisConnection
from common.db.connect import MainDbClientPool
from common.db.db_connection_handler import DbConnectionHandler
from common.models.baseten.answer_extractor import AnswerExtractor, initialize_answer_extractor
from common.models.offensive_query_classifier import (
    OffensiveQueryClassifier,
    initialize_offensive_query_classifier,
)
from common.models.openai.connect import initialize_openai
from common.models.query_classifier import QueryClassifier, initialize_query_classifier
from common.models.question_answer_ranker import (
    QuestionAnswerRanker,
    initialize_question_answer_ranker,
)
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    initialize_similarity_search_embedding_model,
)
from common.models.yes_no_question_classifier import (
    YesNoQuestionClassifier,
    initialize_yes_no_question_classifier,
)
from common.search.connect import AsyncElasticClient, ElasticClient, SearchEnv
from common.storage.connect import StorageClient, init_storage_client
from elasticsearch import AsyncElasticsearch, Elasticsearch
from loguru import logger
from nltk import download as nltk_download
from web.backend.app.config import BackendConfig
from web.services.api import ServicesConnection, init_services_connection


@dataclass(frozen=True)
class Models:
    embedding_model: SimilaritySearchEmbeddingModel
    question_answer_ranker: Optional[QuestionAnswerRanker]
    yes_no_question_classifier: Optional[YesNoQuestionClassifier]
    query_classifier: Optional[QueryClassifier]
    offensive_query_classifier: Optional[OffensiveQueryClassifier]
    answer_extractor: Optional[AnswerExtractor]
    is_openai_initialized: bool


@dataclass(frozen=True)
class SharedState:
    config: BackendConfig
    services: Optional[ServicesConnection]
    db: DbConnectionHandler
    es: Elasticsearch
    async_es: AsyncElasticsearch
    paper_search_async_es: Optional[AsyncElasticsearch]
    storage_client: StorageClient
    redis: redis.Redis
    models: Models


def initialize_models(
    hf_access_token: Optional[str],
    openai_api_key: Optional[str],
    baseten_api_key: Optional[str],
    enable_heavy_models: bool,
) -> Models:
    return Models(
        embedding_model=initialize_similarity_search_embedding_model(),
        question_answer_ranker=(
            initialize_question_answer_ranker(hf_access_token)
            if hf_access_token and enable_heavy_models
            else None
        ),
        yes_no_question_classifier=(
            initialize_yes_no_question_classifier(hf_access_token)
            if hf_access_token and enable_heavy_models
            else None
        ),
        query_classifier=(
            initialize_query_classifier(hf_access_token)
            if hf_access_token and enable_heavy_models
            else None
        ),
        offensive_query_classifier=(
            initialize_offensive_query_classifier(hf_access_token)
            if hf_access_token and enable_heavy_models
            else None
        ),
        is_openai_initialized=(
            initialize_openai(openai_api_key) if openai_api_key and enable_heavy_models else False
        ),
        answer_extractor=(
            initialize_answer_extractor(baseten_api_key) if baseten_api_key else None
        ),
    )


def initialize_shared_state(config: BackendConfig) -> SharedState:
    # Download required NLTK datasets
    nltk_download("stopwords")
    nltk_download("punkt")

    # Disable hugging face tokenization parallelism to avoid deadlock
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    es = ElasticClient(config.search_env)
    async_es = AsyncElasticClient(config.search_env)

    paper_search_async_es = None
    try:
        # If running local env, use same ES instance as primary search
        paper_search_env = config.search_env if config.is_local_env else SearchEnv.PAPER_SEARCH
        paper_search_async_es = AsyncElasticClient(paper_search_env)
    except Exception:
        # Log below whether enabled or disabled
        pass

    db_connection_handler = DbConnectionHandler(
        MainDbClientPool(
            env=config.db_env,
            max_connections=config.db_max_connections,
        )
    )

    shared = SharedState(
        config=config,
        services=(
            init_services_connection(
                host=config.services_host,
                add_auth=not config.is_local_env,
            )
            if config.enable_heavy_models
            else None
        ),
        db=db_connection_handler,
        # Setup elasticsearch connections
        es=es,
        async_es=async_es,
        paper_search_async_es=paper_search_async_es,
        # Setup storage connections
        storage_client=init_storage_client(config.storage_env),
        # Setup redis cache connection
        redis=RedisConnection(config.redis_env),
        models=initialize_models(
            hf_access_token=config.hf_access_token,
            openai_api_key=config.openai_api_key,
            enable_heavy_models=config.enable_heavy_models,
            baseten_api_key=config.baseten_api_key,
        ),
    )
    logger.info(f"Services host: {config.services_host}")
    logger.info(f"Search index id: {config.search_index_id}")
    logger.info(f"Autocomplete index id: {config.autocomplete_index_id}")
    logger.info(f"Enabled reranking: {shared.models.question_answer_ranker is not None}")
    logger.info(f"Enabled yes/no question: {shared.models.yes_no_question_classifier is not None}")
    logger.info(f"Enabled offensive query: {shared.models.offensive_query_classifier is not None}")
    logger.info(f"Enabled query classifier: {shared.models.query_classifier is not None}")
    logger.info(f"Enabled openai endpoints: {shared.models.is_openai_initialized}")
    logger.info(f"Enabled paper search: {shared.paper_search_async_es is not None}")
    logger.info(f"Enabled answer extractor: {shared.models.answer_extractor is not None}")
    logger.info(f"Paper search index id: {config.paper_search_index_id}")
    return shared


async def destroy_shared_state(shared: Optional[SharedState]) -> None:
    if not shared:
        return

    # Shutdown database connections
    shared.db.close()

    # Shutdown elasticsearch connections
    shared.es.close()
    await shared.async_es.close()

    # Shutdown storage connections
    # Nothing to do.

    # Shutdown redis cache connection
    # Nothing to do, redis pool does not need explicit close.
