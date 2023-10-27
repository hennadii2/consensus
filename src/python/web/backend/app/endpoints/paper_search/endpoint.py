from typing import Optional

from common.db.abstract_takeaways import AbstractTakeaways
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.db.papers import Papers
from common.logging.timing import time_endpoint_event
from common.search.async_paper_index import AsyncPaperIndex
from common.search.document_types import StudyTypeKeywordEnum
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.async_wrappers import read_paper, read_paper_badges
from web.backend.app.common.badges import get_primary_author
from web.backend.app.common.cache import (
    TopQueryResults,
    encode_search_cache_id,
    init_paper_search_response_cache,
    init_top_query_results_cache,
    init_used_answers_cache,
    paper_result_to_query_result_data,
)
from web.backend.app.common.data import (
    MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS,
    MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_UI_BAR,
)
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.common.util import dedup_by_first_unique
from web.backend.app.endpoints.paper_search.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    PaperModel,
    PaperSearchResponse,
)
from web.backend.app.endpoints.paper_search.search_util import (
    SearchMethod,
    parse_field_of_study_filters,
    parse_study_type_filters,
    run_search,
)
from web.backend.app.endpoints.search.query_analyzer_util import analyze_query
from web.backend.app.endpoints.summary.data import MIN_NUMBER_RESULTS_TO_SUMMARIZE
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/", response_model=PaperSearchResponse)
async def paper_search(
    request: Request,
    # Query to search
    query: str,
    # Number of results to return
    size: int,
    # Page number of results to return
    page: Optional[int] = None,
    # Min/max years to limit search results within
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    # Study types to limit search to
    study_types: Optional[str] = None,
    # Fields of study to limit search to
    domain: Optional[str] = None,
    # Limits to controlled studies
    controlled: Optional[bool] = None,
    # Limits to human studies
    human: Optional[bool] = None,
    # Min/max sample size to limit search results within
    sample_size_min: Optional[int] = None,
    sample_size_max: Optional[int] = None,
    # Min/max SJR quartile to limit search results within
    sjr_min: Optional[int] = None,
    sjr_max: Optional[int] = None,
    # #####################
    # Testing parameters
    # #####################
    # Testing param: Type of search to run (see options in search_util.py)
    method: Optional[str] = None,
    # Testing param: Sorting weight vector
    sort: Optional[str] = None,
    # Testing param: Number of pages to include in Q/A reranker
    qa_page_count: Optional[int] = None,
    # Testing param: skip cache
    cache_off: Optional[bool] = None,
    # Testing param: Threshold for deciding whether to synthesize or not
    synthesize_threshold: Optional[float] = None,
    # Testing param: Threshold for displaying relevancy label
    relevancy_threshold: Optional[float] = None,
    # Testing param: Provide alternate extract and rerank model ID for testing
    extract_answers_model: Optional[str] = None,
) -> PaperSearchResponse:
    """
    Queries the search index for the string parameter and returns a list of results.
    """
    shared: SharedState = request.app.state.shared

    if shared.paper_search_async_es is None or shared.config.paper_search_index_id is None:
        raise HTTPException(status_code=500, detail=str("Paper search not enabled"))

    if shared.models.answer_extractor is None:
        raise HTTPException(status_code=500, detail=str("Answer extractor not enabled"))

    db = shared.db()
    papers = Papers(db.connection, use_v2=shared.config.use_papers_v2)
    journals = Journals(db.connection)
    journal_scores = JournalScores(db.connection)
    paper_index = AsyncPaperIndex(
        es=shared.paper_search_async_es,
        index_name=shared.config.paper_search_index_id,
    )
    abstract_takeaways = AbstractTakeaways(db.connection)

    disputed = parse_disputed_data(storage_client=shared.storage_client)

    # Search results are cached to speed up previously executed searches
    search_response_cache, search_cache_id = init_paper_search_response_cache(
        full_url=str(request.url),
        search_index_name=shared.config.search_index_id,
        disputed=disputed,
        page=page,
        cache_off=cache_off,
    )
    # Paper answers are cached to skip returning multiple results from the same paper
    used_answers_cache = init_used_answers_cache(
        search_cache_id=search_cache_id,
        page=page,
    )
    # Top result ids are cached to be used in post search synthesis (eg. yes_no)
    top_results_cache = init_top_query_results_cache(
        search_cache_id=search_cache_id,
    )

    # Try to load results from cache
    if search_response_cache is not None:
        try:
            log_load_cache_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.LOAD_CACHE.value,
            )
            cached_response = search_response_cache.read(shared.redis)
            if cached_response is not None:
                log_load_cache_timing_event()
                return cached_response
        except Exception as e:
            logger.exception(e)
            # Fall through to run a new search if cache load fails

    # special case for animal study filter
    parsed_study_types = parse_study_type_filters(study_types)
    filter_animal_studies = None
    if StudyTypeKeywordEnum._ANIMAL_STUDY in parsed_study_types:
        filter_animal_studies = True
        parsed_study_types.remove(StudyTypeKeywordEnum._ANIMAL_STUDY)

    # Run a new search
    try:
        log_analyze_query_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.ANALYZE_QUERY.value,
        )
        query_features = analyze_query(
            query=query,
            shared=shared,
            enable_summary=True,
            enable_yes_no=True,
            use_v2=True,
        )
        log_analyze_query_event()

        # Localhost can only run baseline search, not ELSER
        if method is None:
            method = SearchMethod.DEV_NO_ML.value if shared.config.is_local_env else None

        log_run_search_full_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.RUN_SEARCH_FULL.value,
        )
        results, top_results = await run_search(
            paper_index=paper_index,
            abstract_takeaways=abstract_takeaways,
            question_answer_ranker=shared.models.question_answer_ranker,
            answer_extractor=shared.models.answer_extractor,
            query=query,
            page_size=size,
            page_offset=0 if page is None else page,
            search_method=None if method is None else SearchMethod(method),
            sort=sort,
            qa_page_count=qa_page_count,
            year_min=year_min,
            year_max=year_max,
            limit_to_study_types=parsed_study_types,
            limit_to_fields_of_study=parse_field_of_study_filters(domain),
            filter_controlled_studies=controlled,
            filter_human_studies=human,
            filter_animal_studies=filter_animal_studies,
            sample_size_min=sample_size_min,
            sample_size_max=sample_size_max,
            sjr_best_quartile_min=sjr_min,
            sjr_best_quartile_max=sjr_max,
            extract_answers=query_features.is_synthesizable,
            extract_answers_model=extract_answers_model,
        )
        log_run_search_full_timing_event()

        log_read_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )

        used_answers = used_answers_cache.read(shared.redis)
        unique_results, deduped_results = dedup_by_first_unique(
            items=results,
            # Dedup papers by exact match on answer text
            selector=(lambda x: hash(x.display_text)),
            filter_map=used_answers.hashes,
        )
        for result in deduped_results:
            logger.info(f"Skipping result with used answer: {result}")

        paper_results: list[PaperModel] = []
        for result in unique_results:
            paper = await read_paper(papers=papers, paper_id=result.paper_id)
            if not paper:
                logger.error(
                    f"Skipping search result: unable to find paper with id {result.paper_id}."
                )
                continue

            paper_badges = await read_paper_badges(
                journals=journals,
                journal_scores=journal_scores,
                paper=paper,
                disputed=disputed,
                paper_result=result,
            )

            if result.doc_id is None:
                raise ValueError(f"Failed paper search: missing doc_id for: {paper.id}")
            if result.display_text is None:
                raise ValueError(f"Failed paper search: missing display_text for: {paper.id}")
            if result.url_slug is None:
                raise ValueError(f"Failed paper search: missing url_slug for: {paper.id}")

            paper_results.append(
                PaperModel(
                    paper_id=result.hash_paper_id,
                    doc_id=result.doc_id,
                    display_text=result.display_text,
                    journal=paper.metadata.journal_name,
                    title=paper.metadata.title,
                    primary_author=get_primary_author(
                        list(paper.metadata.author_names),
                    ),
                    authors=list(paper.metadata.author_names),
                    year=paper.metadata.publish_year,
                    url_slug=result.url_slug,
                    doi=paper.metadata.doi,
                    volume=paper.metadata.journal_volume,
                    pages=paper.metadata.journal_pages,
                    badges=paper_badges,
                )
            )
        log_read_db_timing_event()

        # Update cached top results data
        can_synthesize_succeed: Optional[bool] = None
        num_relevant_results: Optional[int] = None
        num_unique_top_results: Optional[int] = None
        if top_results is not None:
            # Remove duplicates with exact same text
            unique_top_results, _ = dedup_by_first_unique(
                selector=lambda x: hash(x.paper.display_text), items=top_results
            )

            # Count number of display relevant results
            num_unique_top_results = len(unique_top_results)
            min_relevance_threshold = (
                relevancy_threshold
                if relevancy_threshold is not None
                else MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_UI_BAR
            )
            num_relevant_results = len(
                list(
                    filter(
                        lambda x: x.relevance >= min_relevance_threshold,
                        unique_top_results,
                    )
                )
            )

            # Count number of synthesizeable results
            min_synthesize_threshold = (
                synthesize_threshold
                if synthesize_threshold is not None
                else MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS
            )
            can_synthesize_succeed = (
                len(
                    list(
                        filter(
                            lambda x: x.relevance >= min_synthesize_threshold,
                            unique_top_results,
                        )
                    )
                )
                >= MIN_NUMBER_RESULTS_TO_SUMMARIZE
            )

            top_results_cache.write(
                shared.redis,
                TopQueryResults(
                    query=query,
                    results=list(
                        map(
                            lambda x: paper_result_to_query_result_data(x.paper),
                            unique_top_results,
                        )
                    ),
                    relevance_scores=list(map(lambda x: x.relevance, unique_top_results)),
                    query_features=query_features,
                ),
            )

        response = PaperSearchResponse(
            search_id=encode_search_cache_id(
                id=search_cache_id,
                obfuscation_encrypt_key=shared.config.obfuscation_encrypt_key,
            ),
            papers=paper_results,
            isEnd=len(results) != size,
            isYesNoQuestion=query_features.is_yes_no_question,
            canSynthesize=query_features.is_synthesizable,
            nuanceRequired=query_features.is_offensive,
            canSynthesizeSucceed=can_synthesize_succeed,
            numTopResults=num_unique_top_results,
            numRelevantResults=num_relevant_results,
        )

        # Update cached response data
        if search_response_cache is not None:
            search_response_cache.write(shared.redis, response)

        # Update cached used paper ids
        used_answers_cache.write(shared.redis, used_answers)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed search for query: '{query}'")
        raise HTTPException(status_code=500, detail=str(e))
