from typing import Optional

from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.journal_scores import JournalScores
from common.db.journals import Journals
from common.db.papers import Papers
from common.logging.timing import time_endpoint_event
from common.search.async_claim_index import AsyncClaimIndex
from common.search.document_types import StudyTypeKeywordEnum
from common.search.paper_util import PaperIdProvider, generate_hash_paper_id
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.async_wrappers import read_claim_badges, read_paper
from web.backend.app.common.badges import get_primary_author
from web.backend.app.common.cache import (
    QueryResults,
    TopQueryResults,
    claim_proto_to_query_result_data,
    encode_search_cache_id,
    init_query_result_data_cache,
    init_search_response_cache,
    init_top_query_results_cache,
    init_used_paper_ids_cache,
)
from web.backend.app.common.data import (
    MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_SYNTHESIS,
    MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_UI_BAR,
)
from web.backend.app.common.disputed import parse_disputed_data
from web.backend.app.common.util import dedup_by_first_unique
from web.backend.app.endpoints.search.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    ClaimModel,
    SearchResponse,
)
from web.backend.app.endpoints.search.query_analyzer_util import analyze_query
from web.backend.app.endpoints.search.search_util import (
    SearchMethod,
    TextCleaningOptions,
    TextType,
    parse_field_of_study_filters,
    parse_study_type_filters,
    run_search,
)
from web.backend.app.endpoints.summary.data import MIN_NUMBER_RESULTS_TO_SUMMARIZE
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/", response_model=SearchResponse)
async def search(
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
    # Testing param: Remove stopwords before search
    stopwords: Optional[str] = None,
    # Testing param: Remove punctuation before search
    punctuation: Optional[str] = None,
    # Testing param: Boost values for claim and title embedding indices
    boost1: Optional[float] = None,
    boost2: Optional[float] = None,
    # Testing param: Number of results to run vector similiarity search against
    rescore_count: Optional[int] = None,
    # Testing param: Number of results to weighted sort against
    sort_count: Optional[int] = None,
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
    # Testing param: If true, synthesize on statements
    synthesize_statements: Optional[bool] = None,
) -> SearchResponse:
    """
    Queries the search index for the string parameter and returns a list of results.
    """
    shared: SharedState = request.app.state.shared

    # TODO(meganvw): Temporarily silently truncate query to try fix latency
    query = query[:300]

    db = shared.db()
    papers = Papers(db.connection, use_v2=shared.config.use_papers_v2)
    journals = Journals(db.connection)
    journal_scores = JournalScores(db.connection)
    claim_index = AsyncClaimIndex(
        es=shared.async_es,
        index_id=shared.config.search_index_id,
    )

    disputed = parse_disputed_data(storage_client=shared.storage_client)

    # Search results are cached to speed up previously executed searches
    search_response_cache, search_cache_id = init_search_response_cache(
        full_url=str(request.url),
        search_index_id=shared.config.search_index_id,
        disputed=disputed,
        page=page,
        cache_off=cache_off,
    )
    # Paper ids are cached to skip returning multiple claims from the same paper
    used_paper_ids_cache = init_used_paper_ids_cache(
        search_cache_id=search_cache_id,
        page=page,
    )
    # Top result ids are cached to be used in post search analysis (eg. yes_no)
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
        log_run_search_full_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.RUN_SEARCH_FULL.value,
        )
        claims, top_claims = await run_search(
            claim_index=claim_index,
            embedding_model=shared.models.embedding_model,
            question_answer_ranker=shared.models.question_answer_ranker,
            query=query,
            page_size=size,
            page_offset=0 if page is None else page,
            search_method=None if method is None else SearchMethod(method),
            text_cleaning_options=TextCleaningOptions(
                remove_stopwords=None if stopwords is None else TextType(stopwords),
                remove_punctuation=None if punctuation is None else TextType(punctuation),
            ),
            boost1=boost1,
            boost2=boost2,
            rescore_count=rescore_count,
            sort_count=sort_count,
            sort=sort,
            year_min=year_min,
            year_max=year_max,
            qa_page_count=qa_page_count,
            known_background_claim_ids=list(disputed.known_background_claim_ids.keys()),
            limit_to_study_types=parsed_study_types,
            limit_to_fields_of_study=parse_field_of_study_filters(domain),
            filter_controlled_studies=controlled,
            filter_human_studies=human,
            filter_animal_studies=filter_animal_studies,
            sample_size_min=sample_size_min,
            sample_size_max=sample_size_max,
            sjr_best_quartile_min=sjr_min,
            sjr_best_quartile_max=sjr_max,
        )
        log_run_search_full_timing_event()

        log_read_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )
        used_paper_ids = used_paper_ids_cache.read(shared.redis)

        # Only allow one result per paper ID in the results.
        # used_paper_ids is cached to dedup by paper id across pages
        unique_claims, deduped_claims = dedup_by_first_unique(
            items=claims,
            selector=(lambda x: x.paper_id),
            filter_map=used_paper_ids.ids,
        )
        for claim in deduped_claims:
            logger.info(f"Skipping claim {claim.id} with used paper id: {claim.paper_id}")

        claim_models: list[ClaimModel] = []
        for claim in unique_claims:
            paper = await read_paper(papers=papers, paper_id=claim.paper_id)
            if paper is None:
                logger.error(
                    f"Skipping search result: unable to find paper with id {claim.paper_id}."
                )
                continue

            badges = await read_claim_badges(
                journals=journals,
                journal_scores=journal_scores,
                paper=paper,
                claim=claim,
                disputed=disputed,
            )

            # NOTE: We generate the ID here instead of querying the DB to avoid
            # effectively doubling DB calls during migration to V2 paper search.
            hash_paper_id = generate_hash_paper_id(PaperIdProvider.S2, claim.paper_id)
            claim_models.append(
                ClaimModel(
                    id=claim.id,
                    paper_id=hash_paper_id,
                    text=claim.metadata.text,
                    journal=paper.metadata.journal_name,
                    title=paper.metadata.title,
                    primary_author=get_primary_author(
                        list(paper.metadata.author_names),
                    ),
                    authors=list(paper.metadata.author_names),
                    year=paper.metadata.publish_year,
                    url_slug=claim.metadata.url_slug,
                    doi=paper.metadata.doi,
                    volume=paper.metadata.journal_volume,
                    pages=paper.metadata.journal_pages,
                    badges=badges,
                )
            )
        log_read_db_timing_event()

        query_features = analyze_query(
            query=query,
            shared=shared,
            enable_summary=True,
            enable_yes_no=True,
            use_v2=False if synthesize_statements is None else synthesize_statements,
        )

        # Update cached top claims data
        can_synthesize_succeed: Optional[bool] = None
        num_relevant_results: Optional[int] = None
        num_unique_top_results: Optional[int] = None
        if top_claims is not None:
            # Remove duplicates with same paper id from top claims
            unique_top_claims, _ = dedup_by_first_unique(
                selector=lambda x: x.claim.paper_id, items=top_claims
            )

            # Count number of display relevant results
            num_unique_top_results = len(unique_top_claims)
            min_relevancy_threshold = (
                relevancy_threshold
                if relevancy_threshold is not None
                else MIN_QA_CLASSIFIER_RELEVANCY_THRESHOLD_FOR_UI_BAR
            )
            num_relevant_results = len(
                list(
                    filter(
                        lambda x: x.relevancy >= min_relevancy_threshold,
                        unique_top_claims,
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
                            lambda x: x.relevancy >= min_synthesize_threshold,
                            unique_top_claims,
                        )
                    )
                )
                >= MIN_NUMBER_RESULTS_TO_SUMMARIZE
            )

            top_results_cache.write(
                shared.redis,
                TopQueryResults(
                    results=list(
                        map(
                            lambda x: claim_proto_to_query_result_data(x.claim),
                            unique_top_claims,
                        )
                    ),
                    relevance_scores=list(map(lambda x: x.relevancy, unique_top_claims)),
                    query=query,
                    query_features=query_features,
                ),
            )

        response = SearchResponse(
            id=encode_search_cache_id(
                id=search_cache_id,
                obfuscation_encrypt_key=shared.config.obfuscation_encrypt_key,
            ),
            claims=claim_models,
            isEnd=len(claims) != size,
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
            query_result_data_cache = init_query_result_data_cache(
                result_ids=",".join([claim.id for claim in unique_claims]),
            )
            query_result_data_cache.write(
                shared.redis,
                QueryResults(
                    results=[claim_proto_to_query_result_data(claim) for claim in unique_claims],
                ),
            )

        # Update cached used paper ids
        used_paper_ids_cache.write(shared.redis, used_paper_ids)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed search for query: '{query}'")
        raise HTTPException(status_code=500, detail=str(e))
