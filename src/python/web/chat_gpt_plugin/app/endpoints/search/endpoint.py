from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.papers import Papers
from common.logging.timing import time_endpoint_event
from common.models.question_answer_ranker import rank_search_results
from common.models.similarity_search_embedding import encode_similarity_search_embedding
from common.search.async_claim_index import AsyncClaimIndex
from common.search.search_util import DEFAULT_SEARCH_CONFIG, make_search_filter
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.concurrency import run_in_threadpool
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from loguru import logger
from typing_extensions import Annotated
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.common.util import dedup_by_first_unique
from web.chat_gpt_plugin.app.endpoints.search.data import (
    ENDPOINT_DESCRIPTION,
    ENDPOINT_SUMMARY,
    LOG_ENDPOINT,
    LOG_EVENTS,
    SearchRequest,
    SearchResponse,
    SearchResponseItem,
)
from web.chat_gpt_plugin.app.endpoints.search.util import init_cache, make_details_url
from web.chat_gpt_plugin.app.state import SharedState

router = APIRouter()


@router.post(
    path="/search",
    response_model=SearchResponse,
    summary=ENDPOINT_SUMMARY,
    description=ENDPOINT_DESCRIPTION,
)
async def search(
    request: Request,
    token: Annotated[HTTPAuthorizationCredentials, Depends(HTTPBearer(auto_error=True))],
    data: SearchRequest,
):
    shared: SharedState = request.app.state.shared

    if token.credentials != shared.config.consensus_auth_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db = shared.db()
    papers = Papers(db.connection, use_v2=True)
    claim_index = AsyncClaimIndex(
        es=shared.async_es,
        index_id=shared.config.search_index_id,
    )
    disputed = parse_disputed_data(storage_client=shared.storage_client)
    known_background_claim_ids = list(disputed.known_background_claim_ids.keys())

    response_cache = init_cache(
        full_url=str(request.url),
        query=data.query,
        disputed=disputed,
    )

    if response_cache is not None:
        log_load_from_cache_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FROM_CACHE.value,
        )
        cached_response = response_cache.read(shared.redis)
        if cached_response is not None:
            log_load_from_cache_event()
            return cached_response

    try:
        log_full_plugin_search = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.FULL_SEARCH.value,
        )
        search_results = await claim_index.query_knn_exact(
            text=data.query,
            embedding=encode_similarity_search_embedding(
                model=shared.models.embedding_model,
                text=data.query,
            ),
            page_offset=0,  # Don't allow pagination for now
            page_size=20,  # Return top 20 results for reranking
            similarity_search_window_size=DEFAULT_SEARCH_CONFIG.vector_search_window_size,
            search_filter=make_search_filter(
                known_background_claim_ids=known_background_claim_ids
            ),
            sort_params=DEFAULT_SEARCH_CONFIG.metadata_sort_params,
            boost_params=DEFAULT_SEARCH_CONFIG.vector_search_boost_params,
        )
        reranked = await run_in_threadpool(
            rank_search_results,
            shared.models.question_answer_ranker,
            search_results,
            data.query,
        )
        # Only allow one result per paper ID in the results.
        # used_paper_ids is cached to dedup by paper id across pages
        results = [x.claim for x in reranked]
        unique_claims, _ = dedup_by_first_unique(
            items=results,
            selector=(lambda x: x.paper_id),
            filter_map=None,
        )

        items: list[SearchResponseItem] = []
        for claim in unique_claims:
            paper = papers.read_by_id(claim.paper_id)
            if not paper:
                logger.error(
                    f"Skipping search result: unable to find paper with id {claim.paper_id}."
                )
                continue

            item = SearchResponseItem(
                claim_text=claim.metadata.text,
                paper_title=paper.metadata.title,
                paper_authors=list(paper.metadata.author_names),
                paper_publish_year=paper.metadata.publish_year,
                publication_journal_name=paper.metadata.journal_name,
                consensus_paper_details_url=make_details_url(
                    claim_id=claim.id,
                    url_slug=claim.metadata.url_slug,
                ),
                doi=paper.metadata.doi,
                volume=paper.metadata.journal_volume,
                pages=paper.metadata.journal_pages,
            )
            items.append(item)

        response = SearchResponse(items=items)
        log_full_plugin_search()

        if response_cache is not None:
            response_cache.write(shared.redis, response)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.error(e)
        raise HTTPException(status_code=500, detail=str(e))
