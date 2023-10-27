from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

from claim_pb2 import Claim
from common.logging.timing import time_endpoint_event
from common.models.question_answer_ranker import (
    QuestionAnswerRanker,
    QuestionAnswerRankerPrediction,
    rank_search_results,
)
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    encode_similarity_search_embedding,
)
from common.search.async_claim_index import AsyncClaimIndex
from common.search.document_types import FieldOfStudyKeywordEnum, StudyTypeKeywordEnum
from common.search.search_util import (
    DEFAULT_SEARCH_CONFIG,
    MultiEmbeddingBoostParams,
    SortParams,
    make_search_filter,
    remove_punctuation,
    remove_stopwords,
)
from fastapi.concurrency import run_in_threadpool
from loguru import logger
from web.backend.app.endpoints.search.data import LOG_ENDPOINT, LOG_EVENTS

# Rerank 20 results by default
DEFAULT_QA_PAGE_RERANKING = 2


class FieldOfStudyFilterShortNames(Enum):
    MEDICINE = "med"
    BIOLOGY = "bio"
    COMPUTER_SCIENCE = "cs"
    CHEMISTRY = "chem"
    PSYCHOLOGY = "psych"
    PHYSICS = "phys"
    MATERIALS_SCIENCE = "mat"
    ENGINEERING = "eng"
    ENVIRONMENTAL_SCIENCE = "env"
    BUSINESS = "bus"
    ECONOMICS = "econ"
    MATHEMATICS = "math"
    POLITICAL_SCIENCE = "poli"
    AGRICULTURE = "agri"
    EDUCATION = "edu"
    SOCIOLOGY = "soc"
    GEOLOGY = "geol"
    GEOGRAPHY = "geog"
    HISTORY = "hist"
    ARTS = "art"
    PHILOSOPHY = "philo"
    LAW = "law"
    LINGUISTICS = "ling"


class StudyTypeFilterShortNames(Enum):
    """
    All supported short names used in the study type filter.
    """

    LITERATURE_REVIEW = "lit_review"
    SYSTEMATIC_REVIEW = "systematic"
    CASE_STUDY = "case"
    META_ANALYSIS = "meta"
    RCT = "rct"
    NON_RCT_EXPERIMENTAL = "non_rct"
    OBSERVATIONAL_STUDY = "observational"
    IN_VITRO_TRIAL = "in_vitro"
    ANIMAL_TRIAL = "animal"


def parse_field_of_study_filters(
    comma_separated_filter_string: Optional[str],
) -> Optional[list[FieldOfStudyKeywordEnum]]:
    """
    Parses the URL friendly (comma separated and shortened) fields of study filter
    string into a list of enums that represent the fields of study values in the
    search index documents.
    """
    if comma_separated_filter_string is None:
        return None
    fields_of_study = []
    for shortened_field_of_study in comma_separated_filter_string.split(","):
        if shortened_field_of_study == FieldOfStudyFilterShortNames.MEDICINE.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.MEDICINE)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.BIOLOGY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.BIOLOGY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.COMPUTER_SCIENCE.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.COMPUTER_SCIENCE)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.CHEMISTRY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.CHEMISTRY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.PSYCHOLOGY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.PSYCHOLOGY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.PHYSICS.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.PHYSICS)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.MATERIALS_SCIENCE.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.MATERIALS_SCIENCE)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.ENGINEERING.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.ENGINEERING)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.ENVIRONMENTAL_SCIENCE.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.ENVIRONMENTAL_SCIENCE)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.BUSINESS.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.BUSINESS)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.ECONOMICS.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.ECONOMICS)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.MATHEMATICS.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.MATHEMATICS)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.POLITICAL_SCIENCE.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.POLITICAL_SCIENCE)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.AGRICULTURE.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.AGRICULTURE)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.EDUCATION.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.EDUCATION)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.SOCIOLOGY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.SOCIOLOGY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.GEOLOGY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.GEOLOGY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.GEOGRAPHY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.GEOGRAPHY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.HISTORY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.HISTORY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.ARTS.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.ARTS)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.PHILOSOPHY.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.PHILOSOPHY)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.LAW.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.LAW)
        elif shortened_field_of_study == FieldOfStudyFilterShortNames.LINGUISTICS.value:
            fields_of_study.append(FieldOfStudyKeywordEnum.LINGUISTICS)
        else:
            logger.warning(f"Unknown field of study filter: {shortened_field_of_study}")
            continue
    return fields_of_study if fields_of_study else None


def parse_study_type_filters(
    comma_separated_filter_string: Optional[str],
) -> list[StudyTypeKeywordEnum]:
    """
    Parses the URL friendly (comma separated and shortened) study type filter
    string into a list of enums that represent the study type values in the
    search index documents.
    """
    if comma_separated_filter_string is None:
        return []
    study_types = []
    for shortened_study_type in comma_separated_filter_string.split(","):
        if shortened_study_type == StudyTypeFilterShortNames.RCT.value:
            study_types.append(StudyTypeKeywordEnum.RCT)
        elif shortened_study_type == StudyTypeFilterShortNames.META_ANALYSIS.value:
            study_types.append(StudyTypeKeywordEnum.META_ANALYSIS)
        elif shortened_study_type == StudyTypeFilterShortNames.SYSTEMATIC_REVIEW.value:
            study_types.append(StudyTypeKeywordEnum.SYSTEMATIC_REVIEW)
        elif shortened_study_type == StudyTypeFilterShortNames.CASE_STUDY.value:
            study_types.append(StudyTypeKeywordEnum.CASE_STUDY)
        elif shortened_study_type == StudyTypeFilterShortNames.NON_RCT_EXPERIMENTAL.value:
            study_types.append(StudyTypeKeywordEnum.NON_RCT_EXPERIMENTAL)
        elif shortened_study_type == StudyTypeFilterShortNames.OBSERVATIONAL_STUDY.value:
            study_types.append(StudyTypeKeywordEnum.NON_RCT_OBSERVATIONAL_STUDY)
        elif shortened_study_type == StudyTypeFilterShortNames.LITERATURE_REVIEW.value:
            study_types.append(StudyTypeKeywordEnum.LITERATURE_REVIEW)
        elif shortened_study_type == StudyTypeFilterShortNames.IN_VITRO_TRIAL.value:
            study_types.append(StudyTypeKeywordEnum.NON_RCT_IN_VITRO)
        elif shortened_study_type == StudyTypeFilterShortNames.ANIMAL_TRIAL.value:
            study_types.append(StudyTypeKeywordEnum._ANIMAL_STUDY)
        else:
            logger.error(f"Unknown study type filter: {shortened_study_type}")
    return study_types


class SearchMethod(Enum):
    """
    All supported experimental search methods.
    """

    KEYWORD = "keyword"
    # Claim embedding search with approximate KNN endpoint
    KNN_APPROX = "approx"
    # Claim embedding search with exact KNN endpoint
    KNN_EXACT = "exact"
    # Claim embedding search with multi exact KNN endpoint
    KNN_MULTI = "multi"


class TextType(Enum):
    """
    Indicate which text type to clean.
    """

    KEYWORD = "keyword"
    # Applied to both keyword search and vector similiarity
    BOTH = "both"


@dataclass(frozen=True)
class TextCleaningOptions:
    """
    All supported experimental text cleaning methods.
    """

    remove_stopwords: Optional[TextType]
    remove_punctuation: Optional[TextType]


def _sort_vector_to_sort_params(
    sort_window_size: Optional[int],
    sort_vector: Optional[str],
) -> Optional[SortParams]:
    if not sort_vector or not sort_window_size:
        return None
    else:
        float_vector = [float(x) for x in sort_vector[1:-1].split(",")]
        return SortParams(
            window_size=sort_window_size,
            similarity_weight=float_vector[0],
            probability_weight=float_vector[1],
            citation_count_weight=float_vector[2],
            citation_count_min=float_vector[6],
            citation_count_max=float_vector[7],
            publish_year_weight=float_vector[3],
            publish_year_min=int(float_vector[4]),
            publish_year_max=int(float_vector[5]),
            best_quartile_weight=float_vector[8],
            best_quartile_default=float_vector[9],
        )


def _generate_embedding(
    embedding_model: SimilaritySearchEmbeddingModel,
    query: str,
) -> list[float]:
    log_generate_embedding_timing_event = time_endpoint_event(
        endpoint=LOG_ENDPOINT,
        event=LOG_EVENTS.ENCODE_EMBEDDING.value,
    )
    embedding = encode_similarity_search_embedding(
        model=embedding_model,
        text=query,
    )
    log_generate_embedding_timing_event()
    return embedding


def _clean_text(
    options: TextCleaningOptions,
    text: str,
) -> Tuple[str, str]:

    keyword_text = text
    vector_text = text

    log_clean_text_timing_event = time_endpoint_event(
        endpoint=LOG_ENDPOINT,
        event=LOG_EVENTS.CLEAN_TEXT.value,
    )
    if options.remove_stopwords is not None:
        keyword_text, vector_text = remove_stopwords(
            keyword_text=keyword_text,
            vector_text=vector_text,
            keyword_only=options.remove_stopwords == TextType.KEYWORD,
        )
    if options.remove_punctuation is not None:
        keyword_text, vector_text = remove_punctuation(
            keyword_text=keyword_text,
            vector_text=vector_text,
            keyword_only=options.remove_punctuation == TextType.KEYWORD,
        )
    log_clean_text_timing_event()

    return (keyword_text, vector_text)


async def _run_search(
    claim_index: AsyncClaimIndex,
    embedding_model: SimilaritySearchEmbeddingModel,
    query: str,
    page_size: int,
    page_offset: int,
    search_method: Optional[SearchMethod],
    text_cleaning_options: TextCleaningOptions,
    boost1: Optional[float],
    boost2: Optional[float],
    rescore_count: Optional[int],
    sort_count: Optional[int],
    sort: Optional[str],
    year_min: Optional[int],
    year_max: Optional[int],
    known_background_claim_ids: list[str],
    limit_to_study_types: list[StudyTypeKeywordEnum],
    limit_to_fields_of_study: Optional[list[FieldOfStudyKeywordEnum]] = None,
    filter_controlled_studies: Optional[bool] = None,
    filter_human_studies: Optional[bool] = None,
    filter_animal_studies: Optional[bool] = None,
    sample_size_min: Optional[int] = None,
    sample_size_max: Optional[int] = None,
    sjr_best_quartile_min: Optional[int] = None,
    sjr_best_quartile_max: Optional[int] = None,
) -> list[Claim]:
    """
    Runs search and parses input for experimental options.

    Raises:
        ValueError: if a known search method is not handled
    """
    search_filter = make_search_filter(
        year_min=year_min,
        year_max=year_max,
        known_background_claim_ids=known_background_claim_ids,
        limit_to_study_types=limit_to_study_types,
        limit_to_fields_of_study=limit_to_fields_of_study,
        filter_controlled_studies=filter_controlled_studies,
        filter_human_studies=filter_human_studies,
        filter_animal_studies=filter_animal_studies,
        sample_size_min=sample_size_min,
        sample_size_max=sample_size_max,
        sjr_best_quartile_min=sjr_best_quartile_min,
        sjr_best_quartile_max=sjr_best_quartile_max,
    )

    if search_method is None:
        # If no search method is specified, use the configured default case
        embedding = _generate_embedding(embedding_model, query)
        results = await claim_index.query_knn_exact(
            text=query,
            embedding=embedding,
            page_size=page_size,
            page_offset=page_offset,
            similarity_search_window_size=DEFAULT_SEARCH_CONFIG.vector_search_window_size,
            search_filter=search_filter,
            sort_params=DEFAULT_SEARCH_CONFIG.metadata_sort_params,
            boost_params=DEFAULT_SEARCH_CONFIG.vector_search_boost_params,
        )
        return results
    elif search_method == SearchMethod.KNN_APPROX:
        _, vector_text = _clean_text(
            options=text_cleaning_options,
            text=query,
        )
        embedding = _generate_embedding(embedding_model, vector_text)
        return await claim_index.query_knn_approximate(embedding=embedding)
    elif search_method == SearchMethod.KNN_EXACT:
        keyword_text, vector_text = _clean_text(
            options=text_cleaning_options,
            text=query,
        )
        embedding = _generate_embedding(embedding_model, vector_text)
        return await claim_index.query_knn_exact(
            text=keyword_text,
            embedding=embedding,
            page_size=page_size,
            page_offset=page_offset,
            similarity_search_window_size=1000 if rescore_count is None else rescore_count,
            search_filter=search_filter,
            sort_params=_sort_vector_to_sort_params(
                sort_window_size=sort_count,
                sort_vector=sort,
            ),
            boost_params=None,
        )
    elif search_method == SearchMethod.KNN_MULTI:
        keyword_text, vector_text = _clean_text(
            options=text_cleaning_options,
            text=query,
        )
        embedding = _generate_embedding(embedding_model, vector_text)
        return await claim_index.query_knn_exact(
            text=keyword_text,
            embedding=embedding,
            page_size=page_size,
            page_offset=page_offset,
            similarity_search_window_size=1000 if rescore_count is None else rescore_count,
            search_filter=search_filter,
            sort_params=_sort_vector_to_sort_params(
                sort_window_size=sort_count,
                sort_vector=sort,
            ),
            boost_params=MultiEmbeddingBoostParams(
                claim_embedding_boost=2 if boost1 is None else boost1,
                title_embedding_boost=1 if boost2 is None else boost2,
            ),
        )
    elif search_method == SearchMethod.KEYWORD:
        keyword_text, _ = _clean_text(
            options=text_cleaning_options,
            text=query,
        )
        return await claim_index.query(
            text=keyword_text,
            page_size=page_size,
            page_offset=page_offset,
        )
    raise ValueError("Failed to run search: unhandled search method {search_method}")


def _rerank(
    question_answer_ranker: QuestionAnswerRanker,
    search_results: list[Claim],
    query: str,
) -> list[QuestionAnswerRankerPrediction]:
    log_qa_rerank_timing_event = time_endpoint_event(
        endpoint=LOG_ENDPOINT,
        event=LOG_EVENTS.QA_RERANK.value,
    )
    reranked = rank_search_results(
        question_answer_ranker,
        results=search_results,
        query=query,
    )
    log_qa_rerank_timing_event()

    return reranked


async def run_search(
    claim_index: AsyncClaimIndex,
    embedding_model: SimilaritySearchEmbeddingModel,
    question_answer_ranker: Optional[QuestionAnswerRanker],
    query: str,
    page_size: int,
    page_offset: int,
    search_method: Optional[SearchMethod],
    text_cleaning_options: TextCleaningOptions,
    boost1: Optional[float],
    boost2: Optional[float],
    rescore_count: Optional[int],
    sort_count: Optional[int],
    sort: Optional[str],
    qa_page_count: Optional[int],
    year_min: Optional[int],
    year_max: Optional[int],
    known_background_claim_ids: list[str],
    limit_to_study_types: list[StudyTypeKeywordEnum],
    limit_to_fields_of_study: Optional[list[FieldOfStudyKeywordEnum]] = None,
    filter_controlled_studies: Optional[bool] = None,
    filter_human_studies: Optional[bool] = None,
    filter_animal_studies: Optional[bool] = None,
    sample_size_min: Optional[int] = None,
    sample_size_max: Optional[int] = None,
    sjr_best_quartile_min: Optional[int] = None,
    sjr_best_quartile_max: Optional[int] = None,
) -> Tuple[list[Claim], Optional[list[QuestionAnswerRankerPrediction]]]:
    """
    Runs search and parses input for experimental options.

    Raises:
        ValueError: if a known search method is not handled
    """
    page_size_modified = page_size
    page_offset_modified = page_offset

    # Check if we should apply reranking to search results
    rerank_top_claims = False
    if question_answer_ranker is not None:
        qa_page_count = (
            DEFAULT_QA_PAGE_RERANKING
            if search_method is None and qa_page_count is None
            else qa_page_count
        )
        if qa_page_count is not None:
            rerank_top_claims = page_offset < qa_page_count
            if rerank_top_claims:
                page_size_modified = page_size * qa_page_count
                page_offset_modified = 0

    log_run_search_timing_event = time_endpoint_event(
        endpoint=LOG_ENDPOINT,
        event=LOG_EVENTS.RUN_SEARCH.value,
    )
    search_results = await _run_search(
        claim_index=claim_index,
        embedding_model=embedding_model,
        query=query,
        page_size=page_size_modified,
        page_offset=page_offset_modified,
        search_method=search_method,
        text_cleaning_options=text_cleaning_options,
        boost1=boost1,
        boost2=boost2,
        rescore_count=rescore_count,
        sort_count=sort_count,
        sort=sort,
        year_min=year_min,
        year_max=year_max,
        known_background_claim_ids=known_background_claim_ids,
        limit_to_study_types=limit_to_study_types,
        limit_to_fields_of_study=limit_to_fields_of_study,
        filter_controlled_studies=filter_controlled_studies,
        filter_human_studies=filter_human_studies,
        filter_animal_studies=filter_animal_studies,
        sample_size_min=sample_size_min,
        sample_size_max=sample_size_max,
        sjr_best_quartile_min=sjr_best_quartile_min,
        sjr_best_quartile_max=sjr_best_quartile_max,
    )
    log_run_search_timing_event()

    current_page_results: list[Claim] = []
    top_claims: Optional[list[QuestionAnswerRankerPrediction]] = None

    if rerank_top_claims and question_answer_ranker is not None:
        reranked = await run_in_threadpool(
            _rerank,
            question_answer_ranker,
            search_results,
            query,
        )

        start = page_offset * page_size
        end = start + page_size

        current_page_results = list(map(lambda x: x.claim, reranked[start:end]))
        if page_offset == 0:
            top_claims = reranked
    else:
        # Create top claims if QA reranking was not run
        current_page_results = search_results
        if page_offset == 0:
            top_claims = list(
                map(
                    lambda x: QuestionAnswerRankerPrediction(claim=x, relevancy=1.0),
                    search_results,
                )
            )

    return (current_page_results, top_claims)
