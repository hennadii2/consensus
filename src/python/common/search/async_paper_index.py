from collections.abc import Mapping
from typing import Any, Optional

from common.search.data import PaperResult
from common.search.paper_util import document_to_paper
from common.search.queries_util import (
    make_elser_query,
    make_paper_keyword_search_query,
    make_paper_sort_rescore_query,
    make_reranking_query,
)
from common.search.search_util import (
    DEFAULT_SEARCH_CONFIG,
    RankingParams,
    SearchFilter,
    SortParams,
)
from elasticsearch import AsyncElasticsearch
from loguru import logger

PAPER_INDEX_FIELD_ELSER_TOKENS = "ml.tokens"


class AsyncPaperIndex:
    """
    Async interface class for working with papers indexed in Elasticsearch.
    """

    def __init__(
        self,
        es: AsyncElasticsearch,
        index_name: str,
    ):
        self.es = es
        self.index_name = index_name

    @property
    def name(self) -> str:
        return self.index_name

    async def exists(self) -> bool:
        result = await self.es.indices.exists(index=self.name)
        return result.body

    async def get_by_hash_paper_id(self, hash_paper_id: str) -> Optional[PaperResult]:
        """
        Returns a paper for the given ID or None if it does not exist.
        """
        term_query = {"term": {"hash_paper_id": {"value": hash_paper_id}}}
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
            logger.error(f"Found > 1 document for id {hash_paper_id}.")

        return document_to_paper(docs[0])

    async def query_elser(
        self,
        query_text: str,
        page_size: int,
        page_offset: int,
        search_filter: SearchFilter,
        ranking_params: Optional[RankingParams],
    ) -> list[PaperResult]:
        es_query = make_elser_query(
            query_text=query_text,
            search_filter=(
                search_filter if search_filter else DEFAULT_SEARCH_CONFIG.search_filter
            ),
            ranking_params=(
                ranking_params if ranking_params else DEFAULT_SEARCH_CONFIG.ranking_params
            ),
        )
        rerankers = []
        if ranking_params is not None:
            rerankers.append(make_reranking_query(ranking_params))

        page_from = page_offset * page_size
        results = await self.es.search(
            size=page_size,
            from_=page_from,
            index=self.name,
            query=es_query,
            rescore=rerankers if rerankers else None,
            track_total_hits=True,  # required optimization for ELSER
            source_excludes=[PAPER_INDEX_FIELD_ELSER_TOKENS],
        )
        return [document_to_paper(doc) for doc in results["hits"]["hits"]]

    async def query(
        self,
        query_text: str,
        page_size: int,
        page_offset: int,
        search_filter: Optional[SearchFilter],
        sort_params: Optional[SortParams],
        debug_paper_id: Optional[str] = None,
    ) -> list[PaperResult]:
        # Keyword search
        keyword_query = make_paper_keyword_search_query(
            query_text=query_text,
            search_filter=(
                search_filter if search_filter else DEFAULT_SEARCH_CONFIG.search_filter
            ),
            debug_paper_id=debug_paper_id,
        )

        rescore: list[Mapping[str, Any]] = []
        # Phase 1 ranking - rank based on citation count, publish year, and best quartile
        if sort_params is not None:
            rescore.append(
                make_paper_sort_rescore_query(
                    window_size=sort_params.window_size,
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
            explain=True if debug_paper_id is not None else False,
        )
        return [document_to_paper(doc) for doc in results["hits"]["hits"]]
