from collections.abc import Mapping
from typing import Any, Optional

from claim_pb2 import Claim
from common.search.claim_index import (
    CLAIM_INDEX_FIELD_EMBEDDING,
    CLAIM_INDEX_FIELD_TITLE_EMBEDDING,
    claim_index_name,
    document_to_claim,
)
from common.search.queries_util import (
    make_keyword_search_query,
    make_similarity_search_rescore_query,
    make_sort_rescore_query,
)
from common.search.search_util import (
    DEFAULT_SEARCH_CONFIG,
    MultiEmbeddingBoostParams,
    SearchFilter,
    SortParams,
)
from elasticsearch import AsyncElasticsearch
from loguru import logger


class AsyncClaimIndex:
    """
    Async interface class for working with ClaimIndexDocuments stored in Elasticsearch.
    """

    def __init__(
        self,
        es: AsyncElasticsearch,
        index_id: str,
    ):
        self.es = es
        self.index_id = index_id

    @property
    def name(self) -> str:
        return claim_index_name(self.index_id)

    async def exists(self) -> bool:
        result = await self.es.indices.exists(index=self.name)
        return result.body

    async def get_by_claim_id(self, claim_id: str) -> Optional[Claim]:
        """
        Returns a claim for the given ID or None if it does not exist.
        """
        term_query = {"term": {"claim_id": {"value": claim_id}}}
        results = await self.es.search(
            size=1,
            index=self.name,
            query=term_query,
        )

        docs = results["hits"]["hits"]
        if not len(docs):
            return None
        if len(docs) > 1:
            # Log error but continue
            logger.error(f"Found > 1 document for id {claim_id}.")

        return document_to_claim(docs[0]["_id"], docs[0])

    async def get_by_claim_ids(self, claim_ids: list[str]) -> dict[str, Optional[Claim]]:
        """
        Returns a dict of claims for each given ID or None if it does not exist.
        """
        if len(claim_ids) <= 0:
            return {}

        term_query = {"terms": {"claim_id": claim_ids}}
        results = await self.es.search(
            size=1,
            index=self.name,
            query=term_query,
        )

        if not len(results["hits"]["hits"]):
            return {}

        known_claims = dict(
            [
                (doc["claim_id"], document_to_claim(doc["_id"], doc))
                for doc in results["hits"]["hits"]
            ]
        )
        return dict(
            [
                (claim_id, known_claims[claim_id] if claim_id in known_claims else None)
                for claim_id in claim_ids
            ]
        )

    async def query(
        self,
        text: str,
        page_size: int = 10,
        page_offset: int = 0,
    ) -> list[Claim]:
        """
        Keyword search and returns a list of claim ids of the results.
        """
        search_query = {"match": {"text": text}}

        page_from = page_offset * page_size
        results = await self.es.search(
            size=page_size,
            from_=page_from,
            index=self.name,
            query=search_query,
            source_excludes=[CLAIM_INDEX_FIELD_EMBEDDING, CLAIM_INDEX_FIELD_TITLE_EMBEDDING],
        )
        return [document_to_claim(doc["_id"], doc) for doc in results["hits"]["hits"]]

    async def query_knn_approximate(
        self,
        embedding: list[float],
        k: int = 10,
        num_candidates: int = 100,
    ) -> list[Claim]:
        """
        Search using k-nearest neighbors for similarity across vector embeddings.
        """
        knn_query = {
            "field": "embedding",
            "query_vector": embedding,
            "k": k,
            "num_candidates": num_candidates,
        }
        results = await self.es.knn_search(
            index=self.name,
            knn=knn_query,
        )
        return [document_to_claim(doc["_id"], doc) for doc in results["hits"]["hits"]]

    async def query_knn_exact(
        self,
        text: str,
        page_size: int,
        page_offset: int,
        similarity_search_window_size: int,
        embedding: list[float],
        search_filter: Optional[SearchFilter],
        sort_params: Optional[SortParams],
        boost_params: Optional[MultiEmbeddingBoostParams],
    ) -> list[Claim]:
        """
        Search using k-nearest neighbors script score rather than knn endpoint.
        """
        keyword_query = make_keyword_search_query(
            text=text,
            search_filter=search_filter if search_filter else DEFAULT_SEARCH_CONFIG.search_filter,
        )

        rescore: list[Mapping[str, Any]] = [
            make_similarity_search_rescore_query(
                query_embedding=embedding,
                window_size=similarity_search_window_size,
                similarity_weight=1 if sort_params is None else sort_params.similarity_weight,
                claim_embedding_boost=None
                if boost_params is None
                else boost_params.claim_embedding_boost,
                title_embedding_boost=None
                if boost_params is None
                else boost_params.title_embedding_boost,
            ),
        ]
        if sort_params is not None:
            rescore.append(
                make_sort_rescore_query(
                    window_size=sort_params.window_size,
                    probability_weight=sort_params.probability_weight,
                    citation_count_weight=sort_params.citation_count_weight,
                    citation_count_min=sort_params.citation_count_min,
                    citation_count_max=sort_params.citation_count_max,
                    publish_year_weight=sort_params.publish_year_weight,
                    publish_year_min=sort_params.publish_year_min,
                    publish_year_max=sort_params.publish_year_max,
                    best_quartile_weight=sort_params.best_quartile_weight,
                    best_quartile_default=sort_params.best_quartile_default,
                )
            )

        page_from = page_offset * page_size
        results = await self.es.search(
            size=page_size,
            from_=page_from,
            index=self.name,
            query=keyword_query,
            rescore=rescore,
            source_excludes=[CLAIM_INDEX_FIELD_EMBEDDING, CLAIM_INDEX_FIELD_TITLE_EMBEDDING],
        )
        return [document_to_claim(doc["_id"], doc) for doc in results["hits"]["hits"]]
