from typing import Optional

from common.db.claim_ids_to_paper_ids import ClaimIdsToPaperIds
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.hash_paper_ids import HashPaperIds
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.db.papers import Papers
from common.logging.timing import time_endpoint_event
from common.search.async_claim_index import AsyncClaimIndex
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.async_wrappers import (
    read_abstract,
    read_claim_badges,
    read_hash_paper_id,
    read_journal_scimago_quartile,
    read_paper,
)
from web.backend.app.common.cache import init_claim_details_response_cache
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.endpoints.claims.details.data import (
    CLAIM_DETAILS_LOG_ENDPOINT,
    EMPTY_RESPONSE,
    LOG_EVENTS,
    ClaimDetails,
    ClaimDetailsResponse,
)
from web.backend.app.endpoints.papers.details.data import JournalDetails, PaperDetails
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/{claim_id}", response_model=ClaimDetailsResponse)
async def claim_details(
    request: Request,
    claim_id: str,
    enable_paper_search: Optional[bool] = None,
):
    """
    Looks up the claim for the given ID and returns all relevant information.
    """
    shared: SharedState = request.app.state.shared
    if enable_paper_search:
        db = shared.db()
        claim_ids_to_paper_ids = ClaimIdsToPaperIds(db.connection)
        hash_paper_ids = HashPaperIds(db.connection)

        claim_id_mapping = claim_ids_to_paper_ids.read_by_claim_id(claim_id)
        if claim_id_mapping is None:
            raise ValueError(
                f"Failed to get claim details: paper not found for claim_id: {claim_id}"
            )
        hash_paper_id = hash_paper_ids.read_hash_paper_id(claim_id_mapping.paper_id)
        if hash_paper_id is None:
            raise ValueError(
                f"Failed to get claim details: hash paper id not found for claim_id: {claim_id_mapping}"  # noqa: E501
            )
        return ClaimDetailsResponse(
            claim=None,
            paper=None,
            paperIdForRedirect=hash_paper_id,
        )

    disputed = parse_disputed_data(storage_client=shared.storage_client)

    claim_details_cache = init_claim_details_response_cache(
        full_url=str(request.url), disputed=disputed
    )
    if claim_details_cache is not None:
        log_load_from_cache_event = time_endpoint_event(
            endpoint=CLAIM_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FROM_CACHE.value,
        )
        cached_response = claim_details_cache.read(shared.redis)
        if cached_response is not None:
            log_load_from_cache_event()
            return cached_response

    db = shared.db()
    papers = Papers(db.connection, use_v2=shared.config.use_papers_v2)
    hash_paper_ids = HashPaperIds(db.connection)
    journals = Journals(db.connection)
    journal_scores = JournalScores(db.connection)
    claim_index = AsyncClaimIndex(
        es=shared.async_es,
        index_id=shared.config.search_index_id,
    )

    try:
        if claim_id in disputed.known_background_claim_ids:
            return EMPTY_RESPONSE

        log_timing_event = time_endpoint_event(
            endpoint=CLAIM_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_CLAIM.value,
        )
        claim = await claim_index.get_by_claim_id(claim_id)
        if claim is None:
            return EMPTY_RESPONSE
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=CLAIM_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )
        paper = await read_paper(papers=papers, paper_id=claim.paper_id)
        if paper is None:
            raise ValueError(f"Failed to get claim details: paper not found: {claim.paper_id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=CLAIM_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_STORAGE.value,
        )
        abstract = await read_abstract(
            storage_client=shared.storage_client,
            paper=paper,
        )
        if abstract is None:
            raise ValueError(f"Failed to get claim details: abstract not found: {paper.id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=CLAIM_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_BADGES.value,
        )
        badges = await read_claim_badges(
            journals=journals,
            journal_scores=journal_scores,
            paper=paper,
            disputed=disputed,
            claim=claim,
        )
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=CLAIM_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_SJR_QUARTILE.value,
        )
        journal_scimago_quartile = await read_journal_scimago_quartile(
            journals=journals, journal_scores=journal_scores, paper=paper
        )
        log_timing_event()

        hash_paper_id = await read_hash_paper_id(
            hash_paper_ids=hash_paper_ids,
            paper_id=claim.paper_id,
        )
        if hash_paper_id is None:
            raise ValueError(
                f"Failed to get claim details: hash paper id not found: {claim.paper_id}"
            )

        response = ClaimDetailsResponse(
            claim=ClaimDetails(
                id=claim_id,
                text=claim.metadata.text,
                url_slug=claim.metadata.url_slug,
            ),
            paper=PaperDetails(
                id=hash_paper_id,
                title=str(paper.metadata.title),
                abstract=abstract,
                abstract_takeaway="",
                authors=list(paper.metadata.author_names),
                citation_count=paper.metadata.citation_count,
                provider_url=paper.metadata.provider_url,
                journal=JournalDetails(
                    title=str(paper.metadata.journal_name),
                    scimago_quartile=journal_scimago_quartile,
                ),
                year=paper.metadata.publish_year,
                doi=paper.metadata.doi,
                volume=paper.metadata.journal_volume,
                pages=paper.metadata.journal_pages,
                badges=badges,
            ),
        )

        claim_details_cache.write(shared.redis, response)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()
        logger.exception(f"Failed to get details for claim: '{claim_id}'")
        raise HTTPException(status_code=500, detail=str(e))
