from enum import Enum
from typing import Optional, Tuple

from common.db.abstract_takeaways import AbstractTakeaway, AbstractTakeaways
from common.logging.timing import time_endpoint_event
from common.models.baseten.answer_extractor import AnswerExtractor, extract_answers_with_rank
from common.models.question_answer_ranker import (
    QuestionAnswerPaperRankerPrediction,
    QuestionAnswerRanker,
    rank_paper_search_results,
)
from common.search.async_paper_index import AsyncPaperIndex
from common.search.data import PaperResult
from common.search.document_types import FieldOfStudyKeywordEnum, StudyTypeKeywordEnum
from common.search.search_util import (
    DEFAULT_SEARCH_CONFIG,
    make_search_filter,
    sort_vector_to_ranking_params,
)
from fastapi.concurrency import run_in_threadpool
from loguru import logger
from web.backend.app.common.async_wrappers import read_abstract_takeaways
from web.backend.app.endpoints.paper_search.data import LOG_ENDPOINT, LOG_EVENTS

# Rerank 20 results by default
DEFAULT_QA_PAGE_RERANKING = 2  # TODO(cvarano): move to DEFAULT_SEARCH_CONFIG


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

    DEFAULT = "default"
    # This should be the same setup as DEFAULT, but allow for url parameter overrides
    TESTING = "p1rank"
    # Maintain a search method for dev testing, since dev has no ML nodes
    DEV_NO_ML = "dev"


async def _run_search(
    paper_index: AsyncPaperIndex,
    query: str,
    page_size: int,
    page_offset: int,
    search_method: Optional[SearchMethod],
    sort: Optional[str],
    year_min: Optional[int],
    year_max: Optional[int],
    limit_to_study_types: list[StudyTypeKeywordEnum],
    limit_to_fields_of_study: Optional[list[FieldOfStudyKeywordEnum]] = None,
    filter_controlled_studies: Optional[bool] = None,
    filter_human_studies: Optional[bool] = None,
    filter_animal_studies: Optional[bool] = None,
    sample_size_min: Optional[int] = None,
    sample_size_max: Optional[int] = None,
    sjr_best_quartile_min: Optional[int] = None,
    sjr_best_quartile_max: Optional[int] = None,
) -> list[PaperResult]:
    """
    Runs search and parses input for experimental options.

    Raises:
        ValueError: if a known search method is not handled
    """
    search_filter = make_search_filter(
        year_min=year_min,
        year_max=year_max,
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

    if search_method is None or search_method == SearchMethod.DEFAULT:
        results = await paper_index.query_elser(
            query_text=query,
            page_size=page_size,
            page_offset=page_offset,
            search_filter=search_filter,
            ranking_params=DEFAULT_SEARCH_CONFIG.ranking_params,
        )
        return results
    # TODO(cvarano): refactor to share common code with DEFAULT
    elif search_method == SearchMethod.TESTING:
        if sort is None:
            ranking_params = DEFAULT_SEARCH_CONFIG.ranking_params
        else:
            ranking_params = sort_vector_to_ranking_params(sort_vector=sort)

        results = await paper_index.query_elser(
            query_text=query,
            page_size=page_size,
            page_offset=page_offset,
            search_filter=search_filter,
            ranking_params=ranking_params,
        )
        return results
    elif search_method == SearchMethod.DEV_NO_ML:
        results = await paper_index.query(
            query_text=query,
            page_size=page_size,
            page_offset=page_offset,
            search_filter=search_filter,
            sort_params=DEFAULT_SEARCH_CONFIG.metadata_sort_params,
        )
        return results
    raise ValueError("Failed to run search: unhandled search method {search_method}")


def _apply_extracted_answers(
    results: list[PaperResult],
    answers: dict[str, Tuple[str, float]],
) -> list[QuestionAnswerPaperRankerPrediction]:
    predictions = []
    for result in results:
        if result.paper_id not in answers:
            logger.warning(f"Missing paper result from answer extractor: {result.paper_id}")
            continue
        answer, prob = answers[result.paper_id]
        result.display_text = answer
        predictions.append(
            QuestionAnswerPaperRankerPrediction(
                paper=result,
                relevance=prob,
            )
        )
    return predictions


async def _extract_answers_with_rank(
    answer_extractor: AnswerExtractor,
    query: str,
    results: list[PaperResult],
    model_override: Optional[str],
) -> list[QuestionAnswerPaperRankerPrediction]:
    answers = await run_in_threadpool(
        extract_answers_with_rank,
        answer_extractor,
        query,
        [(x.paper_id, x.display_text) for x in results],
        model_override,
    )
    return _apply_extracted_answers(results, answers)


def _apply_abstract_takeaways(
    results: list[PaperResult],
    takeaways: list[Optional[AbstractTakeaway]],
) -> list[PaperResult]:
    modified_results = []
    for result, takeaway in zip(results, takeaways):
        if takeaway is not None and takeaway.is_valid_for_product:
            result.display_text = takeaway.takeaway
            modified_results.append(result)
    return modified_results


async def _lookup_abstract_takeaways(
    abstract_takeaways: AbstractTakeaways,
    results: list[PaperResult],
) -> list[PaperResult]:
    takeaways = await read_abstract_takeaways(
        abstract_takeaways=abstract_takeaways,
        paper_ids=[x.paper_id for x in results],
    )
    return _apply_abstract_takeaways(results, takeaways)


async def run_search(
    paper_index: AsyncPaperIndex,
    abstract_takeaways: AbstractTakeaways,
    question_answer_ranker: Optional[QuestionAnswerRanker],
    answer_extractor: AnswerExtractor,
    query: str,
    page_size: int,
    page_offset: int,
    search_method: Optional[SearchMethod],
    sort: Optional[str],
    qa_page_count: Optional[int],
    year_min: Optional[int],
    year_max: Optional[int],
    limit_to_study_types: list[StudyTypeKeywordEnum],
    limit_to_fields_of_study: Optional[list[FieldOfStudyKeywordEnum]] = None,
    filter_controlled_studies: Optional[bool] = None,
    filter_human_studies: Optional[bool] = None,
    filter_animal_studies: Optional[bool] = None,
    sample_size_min: Optional[int] = None,
    sample_size_max: Optional[int] = None,
    sjr_best_quartile_min: Optional[int] = None,
    sjr_best_quartile_max: Optional[int] = None,
    extract_answers: Optional[bool] = None,
    extract_answers_model: Optional[str] = None,
) -> Tuple[list[PaperResult], Optional[list[QuestionAnswerPaperRankerPrediction]]]:
    """
    Runs search and parses input for experimental options.

    Raises:
        ValueError: if a known search method is not handled
    """
    page_size_modified = page_size
    page_offset_modified = page_offset

    # TODO(cvarano): Clean up logic to account for answer_extractor
    # Check if we should apply reranking to search results
    rerank_top_results = False
    if question_answer_ranker is not None:
        qa_page_count = (
            DEFAULT_QA_PAGE_RERANKING
            if search_method is None and qa_page_count is None
            else qa_page_count
        )
        if qa_page_count is not None:
            rerank_top_results = page_offset < qa_page_count
            if rerank_top_results:
                page_size_modified = page_size * qa_page_count
                page_offset_modified = 0

    log_timing_event = time_endpoint_event(
        endpoint=LOG_ENDPOINT,
        event=LOG_EVENTS.RUN_SEARCH.value,
    )
    search_results = await _run_search(
        paper_index=paper_index,
        query=query,
        page_size=page_size_modified,
        page_offset=page_offset_modified,
        search_method=search_method,
        sort=sort,
        year_min=year_min,
        year_max=year_max,
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
    log_timing_event()

    current_page_results: list[PaperResult] = search_results
    top_results: Optional[list[QuestionAnswerPaperRankerPrediction]] = None

    if extract_answers:
        log_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.EXTRACT_ANSWERS_AND_RERANK.value,
        )
        answers_with_relevance_score = await _extract_answers_with_rank(
            answer_extractor=answer_extractor,
            query=query,
            results=search_results,
            model_override=extract_answers_model,
        )
        log_timing_event()

        if rerank_top_results:
            answers_with_relevance_score = sorted(
                answers_with_relevance_score,
                key=lambda item: item.relevance,
                reverse=True,
            )

            start = page_offset * page_size
            end = start + page_size
            current_page_results = list(
                map(lambda x: x.paper, answers_with_relevance_score[start:end])
            )
        else:
            current_page_results = list(map(lambda x: x.paper, answers_with_relevance_score))

        if page_offset == 0:
            top_results = answers_with_relevance_score

        return (current_page_results, top_results)
    else:
        # Set abstract takeways as paper display text before re-ranking
        log_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.LOOKUP_ABSTRACT_TAKEAWAYS.value,
        )
        search_results = await _lookup_abstract_takeaways(
            abstract_takeaways=abstract_takeaways,
            results=search_results,
        )
        log_timing_event()

        if rerank_top_results and question_answer_ranker is not None:
            log_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.QA_RERANK.value,
            )
            reranked = rank_paper_search_results(
                question_answer_ranker,
                results=search_results,
                query=query,
            )
            log_timing_event()

            start = page_offset * page_size
            end = start + page_size

            current_page_results = list(map(lambda x: x.paper, reranked[start:end]))
            if page_offset == 0:
                top_results = reranked

        return (current_page_results, top_results)
