from typing import Optional

from common.db.abstract_takeaways import AbstractTakeaways
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.hash_paper_ids import HashPaperIds
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.db.papers import Papers
from common.logging.timing import time_endpoint_event
from common.search.async_paper_index import AsyncPaperIndex
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.async_wrappers import (
    read_abstract,
    read_abstract_takeaway,
    read_journal_scimago_quartile,
    read_paper,
    read_paper_badges,
    read_paper_id,
)
from web.backend.app.common.cache import init_paper_details_response_cache
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.endpoints.papers.details.data import (
    LOG_EVENTS,
    PAPER_DETAILS_LIST_LOG_ENDPOINT,
    PAPER_DETAILS_LOG_ENDPOINT,
    JournalDetails,
    PaperDetails,
    PaperDetailsListResponse,
    PaperDetailsResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/{hash_paper_id}", response_model=PaperDetailsResponse)
async def paper_details(
    request: Request,
    hash_paper_id: str,
    enable_paper_search: Optional[bool] = None,
):
    """
    Looks up the paper for the given ID and returns all relevant information.
    """
    shared: SharedState = request.app.state.shared
    if shared.paper_search_async_es is None or shared.config.paper_search_index_id is None:
        raise HTTPException(status_code=500, detail=str("Paper search not enabled"))

    disputed = parse_disputed_data(storage_client=shared.storage_client)

    # Try to load response from cache
    paper_details_cache = init_paper_details_response_cache(
        full_url=str(request.url), disputed=disputed
    )
    if paper_details_cache is not None:
        log_load_from_cache_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.LOAD_FROM_CACHE.value,
        )
        cached_response = paper_details_cache.read(shared.redis)
        if cached_response is not None:
            log_load_from_cache_event()
            return cached_response

    db = shared.db()
    abstract_takeaways = AbstractTakeaways(db.connection)
    papers = Papers(db.connection, use_v2=shared.config.use_papers_v2)
    hash_paper_ids = HashPaperIds(db.connection)
    journals = Journals(db.connection)
    journal_scores = JournalScores(db.connection)

    paper_index = (
        AsyncPaperIndex(
            es=shared.paper_search_async_es,
            index_name=shared.config.paper_search_index_id,
        )
        if enable_paper_search or shared.config.paper_search_index_id_on_claim_cluster is None
        else AsyncPaperIndex(
            es=shared.async_es,
            index_name=shared.config.paper_search_index_id_on_claim_cluster,
        )
    )

    try:
        log_timing_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )

        # TODO(meganvw): Write join SQL query to directly read_paper by hash_paper_id.
        paper_id = await read_paper_id(
            hash_paper_ids=hash_paper_ids,
            hash_paper_id=hash_paper_id,
        )
        if paper_id is None:
            raise ValueError(f"Failed to get paper details: paper id not found: {hash_paper_id}")
        paper = await read_paper(papers=papers, paper_id=paper_id)
        if paper is None:
            raise ValueError(f"Failed to get paper details: paper not found: {paper_id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_STORAGE.value,
        )
        abstract = await read_abstract(
            storage_client=shared.storage_client,
            paper=paper,
        )
        if abstract is None:
            raise ValueError(f"Failed to get paper details: abstract not found: {paper.id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_ABSTRACT_TAKEAWAY.value,
        )
        abstract_takeaway = await read_abstract_takeaway(
            abstract_takeaways=abstract_takeaways,
            paper_id=paper_id,
        )
        if abstract_takeaway is None or not abstract_takeaway.is_valid_for_product:
            raise ValueError(
                f"Failed to get paper details: abstract takeaway not found: {paper_id}"
            )
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_PAPER.value,
        )

        paper_result = await paper_index.get_by_hash_paper_id(hash_paper_id)
        if paper_result is None:
            raise ValueError(f"Failed to get paper details: paper result not found: {paper_id}")
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_BADGES.value,
        )
        badges = await read_paper_badges(
            journals=journals,
            journal_scores=journal_scores,
            paper=paper,
            disputed=disputed,
            paper_result=paper_result,
        )
        log_timing_event()

        log_timing_event = time_endpoint_event(
            endpoint=PAPER_DETAILS_LOG_ENDPOINT,
            event=LOG_EVENTS.READ_SJR_QUARTILE.value,
        )
        journal_scimago_quartile = await read_journal_scimago_quartile(
            journals=journals, journal_scores=journal_scores, paper=paper
        )
        log_timing_event()

        response = PaperDetailsResponse(
            abstract=abstract,
            abstract_takeaway=abstract_takeaway.takeaway,
            authors=list(paper.metadata.author_names),
            badges=badges,
            citation_count=paper.metadata.citation_count,
            doi=paper.metadata.doi,
            id=hash_paper_id,
            journal=JournalDetails(
                title=str(paper.metadata.journal_name),
                scimago_quartile=journal_scimago_quartile,
            ),
            pages=paper.metadata.journal_pages,
            provider_url=paper.metadata.provider_url,
            title=str(paper.metadata.title),
            volume=paper.metadata.journal_volume,
            url_slug=paper_result.url_slug,
            year=paper.metadata.publish_year,
        )

        paper_details_cache.write(shared.redis, response)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()
        logger.exception(f"Failed to get details for paper: '{hash_paper_id}'")
        raise HTTPException(status_code=500, detail=str(e))


# TODO(jimmy): Extract the shared logic between the two apis into a shared function.
@router.get("/", response_model=PaperDetailsListResponse)
async def paper_details_list(
    request: Request,
    paper_ids: str,
    include_abstract: bool = False,
    include_journal: bool = False,
    enable_paper_search: Optional[bool] = None,
):
    """
    Looks up the details for the given paper IDs and returns all relevant information.
    """
    shared: SharedState = request.app.state.shared
    if shared.paper_search_async_es is None or shared.config.paper_search_index_id is None:
        raise HTTPException(status_code=500, detail=str("Paper search not enabled"))

    disputed = parse_disputed_data(storage_client=shared.storage_client)

    db = shared.db()
    abstract_takeaways = AbstractTakeaways(db.connection)
    papers = Papers(db.connection, use_v2=shared.config.use_papers_v2)
    hash_paper_ids = HashPaperIds(db.connection)
    journals = Journals(db.connection)
    journal_scores = JournalScores(db.connection)
    paper_index = (
        AsyncPaperIndex(
            es=shared.paper_search_async_es,
            index_name=shared.config.paper_search_index_id,
        )
        if enable_paper_search or shared.config.paper_search_index_id_on_claim_cluster is None
        else AsyncPaperIndex(
            es=shared.async_es,
            index_name=shared.config.paper_search_index_id_on_claim_cluster,
        )
    )

    try:
        response = PaperDetailsListResponse(paperDetailsListByPaperId={})
        if len(paper_ids.strip()) <= 0:
            return response

        ids = paper_ids.split(",")

        # TODO(jimmy): Optimize by doing all DB and ES reads together
        for hash_paper_id in ids:

            log_timing_event = time_endpoint_event(
                endpoint=PAPER_DETAILS_LIST_LOG_ENDPOINT,
                event=LOG_EVENTS.READ_DB.value,
            )
            # TODO(meganvw): Write join SQL query to directly read_paper by hash_paper_id.
            paper_id = await read_paper_id(
                hash_paper_ids=hash_paper_ids,
                hash_paper_id=hash_paper_id,
            )
            if paper_id is None:
                raise ValueError(
                    f"Failed to get paper details: paper id not found: {hash_paper_id}"
                )
            paper = await read_paper(papers=papers, paper_id=paper_id)
            if paper is None:
                raise ValueError(f"Failed to get paper details: paper not found: {paper_id}")
            log_timing_event()

            if include_abstract:
                log_timing_event = time_endpoint_event(
                    endpoint=PAPER_DETAILS_LIST_LOG_ENDPOINT,
                    event=LOG_EVENTS.READ_STORAGE.value,
                )
                abstract = await read_abstract(
                    storage_client=shared.storage_client,
                    paper=paper,
                )
                if abstract is None:
                    raise ValueError(
                        f"Failed to get paper details: abstract not found: {paper.id}"
                    )
                log_timing_event()
            else:
                abstract = None

            log_timing_event = time_endpoint_event(
                endpoint=PAPER_DETAILS_LIST_LOG_ENDPOINT,
                event=LOG_EVENTS.READ_ABSTRACT_TAKEAWAY.value,
            )
            abstract_takeaway = await read_abstract_takeaway(
                abstract_takeaways=abstract_takeaways,
                paper_id=paper_id,
            )
            if abstract_takeaway is None or not abstract_takeaway.is_valid_for_product:
                raise ValueError(
                    f"Failed to get paper details: abstract takeaway not found: {paper_id}"
                )
            log_timing_event()

            log_timing_event = time_endpoint_event(
                endpoint=PAPER_DETAILS_LIST_LOG_ENDPOINT,
                event=LOG_EVENTS.READ_PAPER.value,
            )

            paper_result = await paper_index.get_by_hash_paper_id(hash_paper_id)
            if paper_result is None:
                raise ValueError(
                    f"Failed to get paper details: paper result not found: {paper_id}"
                )
            log_timing_event()

            log_timing_event = time_endpoint_event(
                endpoint=PAPER_DETAILS_LIST_LOG_ENDPOINT,
                event=LOG_EVENTS.READ_BADGES.value,
            )
            badges = await read_paper_badges(
                journals=journals,
                journal_scores=journal_scores,
                paper=paper,
                disputed=disputed,
                paper_result=paper_result,
            )
            log_timing_event()

            if include_journal:
                log_timing_event = time_endpoint_event(
                    endpoint=PAPER_DETAILS_LIST_LOG_ENDPOINT,
                    event=LOG_EVENTS.READ_SJR_QUARTILE.value,
                )
                journal_scimago_quartile = await read_journal_scimago_quartile(
                    journals=journals, journal_scores=journal_scores, paper=paper
                )
                log_timing_event()
            else:
                journal_scimago_quartile = None

            paper_details = PaperDetails(
                abstract=abstract,
                abstract_takeaway=abstract_takeaway.takeaway,
                authors=list(paper.metadata.author_names),
                badges=badges,
                citation_count=paper.metadata.citation_count,
                doi=paper.metadata.doi,
                id=hash_paper_id,
                journal=JournalDetails(
                    title=str(paper.metadata.journal_name),
                    scimago_quartile=journal_scimago_quartile,
                ),
                pages=paper.metadata.journal_pages,
                provider_url=paper.metadata.provider_url,
                title=str(paper.metadata.title),
                volume=paper.metadata.journal_volume,
                url_slug=paper_result.url_slug,
                year=paper.metadata.publish_year,
            )

            response.paperDetailsListByPaperId[hash_paper_id] = paper_details

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()
        logger.exception(f"Failed to get details list for paper ids: '{paper_ids}'")
        raise HTTPException(status_code=500, detail=str(e))
