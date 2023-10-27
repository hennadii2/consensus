import string
from dataclasses import asdict as dataclass_to_dict
from dataclasses import dataclass
from typing import Optional, Tuple

import nltk
import numpy as np
from common.search.document_types import FieldOfStudyKeywordEnum, StudyTypeKeywordEnum
from nltk.corpus import stopwords
from nltk.tokenize import TreebankWordDetokenizer, word_tokenize  # type: ignore

nltk.download("punkt")

NLTK_OPEN_QUOTE = "``"
NLTK_CLOSE_QUOTE = "''"
QUANTIZE_SCALE_FACTOR = 470
# Used in text cleaning
REMOVE_PUNCTUATION_TRANSLATION = str.maketrans("", "", string.punctuation)


@dataclass(frozen=True)
class SearchFilter:
    year_min: Optional[int]
    year_max: Optional[int]
    # Known background claim IDs that should be removed at data science level
    known_background_claim_ids: list[str]
    limit_to_study_types: list[StudyTypeKeywordEnum]
    limit_to_fields_of_study: Optional[list[FieldOfStudyKeywordEnum]] = None
    filter_controlled_studies: Optional[bool] = None
    filter_human_studies: Optional[bool] = None
    filter_animal_studies: Optional[bool] = None
    sample_size_min: Optional[int] = None
    sample_size_max: Optional[int] = None
    sjr_best_quartile_min: Optional[int] = None
    sjr_best_quartile_max: Optional[int] = None
    # Known background paper IDs that should be removed at data science level
    known_background_paper_ids: Optional[list[str]] = None


# TODO(cvarano): simplify ranking params config flow (#1308)
@dataclass(frozen=True)
class RankingParams:
    # Top-k query results to apply ranking to
    window_size: int
    # Ranking weights for original relevance score and reranking score
    original_weight: float
    reranking_weight: float
    # Exponential decay params for publish_year
    publish_year_default: Optional[int] = None
    publish_year_origin: Optional[int] = None
    publish_year_scale: Optional[float] = None
    publish_year_offset: Optional[float] = None
    publish_year_decay: Optional[float] = None
    # Default value to impute for SJR best quartile when missing
    best_quartile_default: Optional[float] = None
    # Feature weights
    best_quartile_weight: Optional[float] = None
    publish_year_weight: Optional[float] = None
    study_type_weight: Optional[float] = None
    sjr_cite_weight: Optional[float] = None
    cite_weight: Optional[float] = None
    age_weight_0: Optional[float] = None  # < 1yr old
    age_weight_1: Optional[float] = None  # < 2yrs
    age_weight_2: Optional[float] = None  # < 3yrs
    age_weight_3: Optional[float] = None  # 3yrs < age < 9yrs
    age_weight_4: Optional[float] = None  # age > 9yrs
    kw_recall_weight: Optional[float] = None
    kw_boost_weight: Optional[float] = None


@dataclass(frozen=True)
class SortParams:
    # Number of results to apply sorting
    window_size: int
    # Weight to apply to similiarity search results
    similarity_weight: float
    # Weight to apply to claim probability in sort
    probability_weight: float
    # Weight to apply to citation count in sort
    citation_count_weight: float
    # Minimum and maximum bounds for normalizing citation count between [0, 1]
    citation_count_min: float
    citation_count_max: float
    # Weight to apply to publishing year in sort
    publish_year_weight: float
    # Minimum and maximum bounds for normalizing publish year between [0, 1]
    publish_year_min: int
    publish_year_max: int
    # Weight to apply to SJR best quartile in sort
    best_quartile_weight: float
    # Default value to use for SJR best quartile when not available
    best_quartile_default: float


@dataclass(frozen=True)
class MultiEmbeddingBoostParams:
    claim_embedding_boost: float
    title_embedding_boost: float


@dataclass(frozen=True)
class DefaultSearchConfig:
    vector_search_window_size: int
    vector_search_boost_params: MultiEmbeddingBoostParams
    metadata_sort_params: SortParams
    search_filter: SearchFilter
    ranking_params: RankingParams


DEFAULT_SEARCH_CONFIG = DefaultSearchConfig(
    vector_search_window_size=2500,
    vector_search_boost_params=MultiEmbeddingBoostParams(
        claim_embedding_boost=4,
        title_embedding_boost=1,
    ),
    metadata_sort_params=SortParams(
        window_size=125,
        similarity_weight=1,
        probability_weight=0.15,
        citation_count_weight=0.15,
        citation_count_min=0,
        citation_count_max=10,
        publish_year_weight=0.05,
        publish_year_min=1970,
        publish_year_max=2022,
        best_quartile_weight=0.15,
        best_quartile_default=3,
    ),
    search_filter=SearchFilter(
        year_min=None,
        year_max=None,
        known_background_claim_ids=[],
        limit_to_study_types=[],
        limit_to_fields_of_study=None,
        filter_controlled_studies=None,
        filter_human_studies=None,
        filter_animal_studies=None,
        sample_size_min=None,
        sample_size_max=None,
        sjr_best_quartile_min=None,
        sjr_best_quartile_max=None,
    ),
    ranking_params=RankingParams(
        window_size=125,
        original_weight=1.0,
        reranking_weight=1.0,
        publish_year_default=1970,
        publish_year_origin=2023,
        publish_year_scale=0.0,
        publish_year_offset=0.0,
        publish_year_decay=0.0,
        best_quartile_default=3,
        best_quartile_weight=0.15,
        publish_year_weight=0.05,
        study_type_weight=0.0,
        sjr_cite_weight=0.02,
        cite_weight=0.0,
        age_weight_0=0.7,
        age_weight_1=0.4,
        age_weight_2=0.27,
        age_weight_3=0.23,
        age_weight_4=0.18,
        kw_recall_weight=0.05,
        kw_boost_weight=0.25,
    ),
)


def make_ranking_params(
    window_size: Optional[int] = None,
    original_weight: Optional[float] = None,
    reranking_weight: Optional[float] = None,
    publish_year_default: Optional[int] = None,
    publish_year_origin: Optional[int] = None,
    publish_year_scale: Optional[float] = None,
    publish_year_offset: Optional[float] = None,
    publish_year_decay: Optional[float] = None,
    best_quartile_default: Optional[float] = None,
    best_quartile_weight: Optional[float] = None,
    publish_year_weight: Optional[float] = None,
    study_type_weight: Optional[float] = None,
    sjr_cite_weight: Optional[float] = None,
    cite_weight: Optional[float] = None,
    age_weight_0: Optional[float] = None,
    age_weight_1: Optional[float] = None,
    age_weight_2: Optional[float] = None,
    age_weight_3: Optional[float] = None,
    age_weight_4: Optional[float] = None,
    kw_recall_weight: Optional[float] = None,
    kw_boost_weight: Optional[float] = None,
) -> RankingParams:
    added_params = {k: v for k, v in locals().items() if v is not None}
    ranking_params = dataclass_to_dict(DEFAULT_SEARCH_CONFIG.ranking_params)
    ranking_params.update(added_params)
    return RankingParams(**ranking_params)


def make_search_filter(
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    known_background_claim_ids: Optional[list[str]] = None,
    limit_to_study_types: Optional[list[StudyTypeKeywordEnum]] = None,
    limit_to_fields_of_study: Optional[list[FieldOfStudyKeywordEnum]] = None,
    filter_controlled_studies: Optional[bool] = None,
    filter_human_studies: Optional[bool] = None,
    filter_animal_studies: Optional[bool] = None,
    sample_size_min: Optional[int] = None,
    sample_size_max: Optional[int] = None,
    sjr_best_quartile_min: Optional[int] = None,
    sjr_best_quartile_max: Optional[int] = None,
    known_background_paper_ids: Optional[list[str]] = None,
) -> SearchFilter:
    added_filters = {k: v for k, v in locals().items() if v is not None}
    search_filters = dataclass_to_dict(DEFAULT_SEARCH_CONFIG.search_filter)
    search_filters.update(added_filters)
    return SearchFilter(**search_filters)


def extract_phrases(query_text: str) -> list[str]:
    phrases: list[str] = []
    if '"' not in query_text:
        return phrases

    tokens = word_tokenize(query_text)
    open_quotes_indices = []
    close_quotes_indices = []
    for idx, token in enumerate(tokens):
        if token == NLTK_OPEN_QUOTE:
            open_quotes_indices.append(idx)
        elif token == NLTK_CLOSE_QUOTE:
            close_quotes_indices.append(idx)
    for open_quote_idx, close_quote_idx in zip(open_quotes_indices, close_quotes_indices):
        phrase_start = open_quote_idx + 1
        phrases.append(
            str(TreebankWordDetokenizer().detokenize(tokens[phrase_start:close_quote_idx]))
        )
    return phrases


def sort_vector_to_ranking_params(
    sort_vector: str,
) -> RankingParams:
    # parse sort vector from string of fmt "[x,y,z]"
    param_vector = [float(x) for x in sort_vector[1:-1].split(",")]
    return RankingParams(
        window_size=int(param_vector[0]),
        original_weight=param_vector[1],
        reranking_weight=param_vector[2],
        publish_year_default=int(param_vector[3]),
        publish_year_origin=int(param_vector[4]),
        publish_year_scale=param_vector[5],
        publish_year_offset=param_vector[6],
        publish_year_decay=param_vector[7],
        best_quartile_default=param_vector[8],
        best_quartile_weight=param_vector[9],
        publish_year_weight=param_vector[10],
        study_type_weight=param_vector[11],
        sjr_cite_weight=param_vector[12],
        cite_weight=param_vector[13],
        age_weight_0=param_vector[14],
        age_weight_1=param_vector[15],
        age_weight_2=param_vector[16],
        age_weight_3=param_vector[17],
        age_weight_4=param_vector[18],
        kw_recall_weight=param_vector[19],
        kw_boost_weight=param_vector[20],
    )


def _remove_punctuation(text: str) -> str:
    """Removes punctuation from input text."""
    return text.translate(REMOVE_PUNCTUATION_TRANSLATION)


def remove_punctuation(
    keyword_text: str,
    vector_text: str,
    keyword_only: bool,
) -> Tuple[str, str]:
    """
    Helper to simplify code paths when applying punctuation removal separately
    to text meant for keyword or vector search.
    """
    if keyword_only:
        return (_remove_punctuation(keyword_text), vector_text)
    else:
        return (_remove_punctuation(keyword_text), _remove_punctuation(vector_text))


def _remove_stopwords(text: str) -> str:
    """Removes stopwords from input text."""
    return " ".join([x for x in text.split() if x not in stopwords.words("english")])


def remove_stopwords(
    keyword_text: str,
    vector_text: str,
    keyword_only: bool,
) -> Tuple[str, str]:
    """
    Helper to simplify code paths when applying stopwords removal separately
    to text meant for keyword or vector search.
    """
    if keyword_only:
        return (_remove_stopwords(keyword_text), vector_text)
    else:
        return (_remove_stopwords(keyword_text), _remove_stopwords(vector_text))


def quantize_vector(vector: list[float]) -> list[int]:
    quantized_vector = (
        np.around(np.array(vector) * QUANTIZE_SCALE_FACTOR).clip(-128, 127).astype(int)
    )
    return quantized_vector.tolist()  # type: ignore [no-any-return]
