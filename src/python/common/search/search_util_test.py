from common.search.document_types import FieldOfStudyKeywordEnum, StudyTypeKeywordEnum
from common.search.search_util import (
    DEFAULT_SEARCH_CONFIG,
    RankingParams,
    SearchFilter,
    extract_phrases,
    make_ranking_params,
    make_search_filter,
    remove_punctuation,
    remove_stopwords,
    sort_vector_to_ranking_params,
)
from nltk import download as nltk_download

nltk_download("stopwords")


def test_make_search_filter() -> None:
    actual = make_search_filter()
    assert actual == DEFAULT_SEARCH_CONFIG.search_filter

    actual = make_search_filter(
        year_min=2000,
        year_max=2020,
    )
    assert actual == SearchFilter(
        year_min=2000,
        year_max=2020,
        known_background_claim_ids=[],
        limit_to_study_types=[],
        filter_controlled_studies=None,
        filter_human_studies=None,
        sample_size_min=None,
        sample_size_max=None,
        sjr_best_quartile_min=None,
        sjr_best_quartile_max=None,
    )

    actual = make_search_filter(
        known_background_claim_ids=["claim1", "claim2"],
        limit_to_study_types=[StudyTypeKeywordEnum.RCT, StudyTypeKeywordEnum.OTHER],
        limit_to_fields_of_study=[
            FieldOfStudyKeywordEnum.MEDICINE,
            FieldOfStudyKeywordEnum.BIOLOGY,
        ],
    )
    assert actual == SearchFilter(
        year_min=None,
        year_max=None,
        known_background_claim_ids=["claim1", "claim2"],
        limit_to_study_types=[StudyTypeKeywordEnum.RCT, StudyTypeKeywordEnum.OTHER],
        limit_to_fields_of_study=[
            FieldOfStudyKeywordEnum.MEDICINE,
            FieldOfStudyKeywordEnum.BIOLOGY,
        ],
        filter_controlled_studies=None,
        filter_human_studies=None,
        sample_size_min=None,
        sample_size_max=None,
        sjr_best_quartile_min=None,
        sjr_best_quartile_max=None,
    )

    actual = make_search_filter(
        filter_controlled_studies=True,
        filter_human_studies=True,
    )
    assert actual == SearchFilter(
        year_min=None,
        year_max=None,
        known_background_claim_ids=[],
        limit_to_study_types=[],
        filter_controlled_studies=True,
        filter_human_studies=True,
        sample_size_min=None,
        sample_size_max=None,
        sjr_best_quartile_min=None,
        sjr_best_quartile_max=None,
    )


def test_make_ranking_params() -> None:
    actual = make_ranking_params()
    assert actual == DEFAULT_SEARCH_CONFIG.ranking_params

    actual = make_ranking_params(
        window_size=300,
        original_weight=0.5,
        best_quartile_default=4,
    )
    assert actual == RankingParams(
        window_size=300,
        original_weight=0.5,
        reranking_weight=DEFAULT_SEARCH_CONFIG.ranking_params.reranking_weight,
        publish_year_default=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_default,
        publish_year_origin=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_origin,
        publish_year_scale=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_scale,
        publish_year_offset=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_offset,
        publish_year_decay=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_decay,
        best_quartile_default=4,
        best_quartile_weight=DEFAULT_SEARCH_CONFIG.ranking_params.best_quartile_weight,
        publish_year_weight=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_weight,
        study_type_weight=DEFAULT_SEARCH_CONFIG.ranking_params.study_type_weight,
        sjr_cite_weight=DEFAULT_SEARCH_CONFIG.ranking_params.sjr_cite_weight,
        cite_weight=DEFAULT_SEARCH_CONFIG.ranking_params.cite_weight,
        age_weight_0=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_0,
        age_weight_1=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_1,
        age_weight_2=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_2,
        age_weight_3=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_3,
        age_weight_4=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_4,
        kw_recall_weight=DEFAULT_SEARCH_CONFIG.ranking_params.kw_recall_weight,
        kw_boost_weight=DEFAULT_SEARCH_CONFIG.ranking_params.kw_boost_weight,
    )

    actual = make_ranking_params(
        publish_year_default=1950,
        publish_year_origin=2020,
        reranking_weight=0.2,
        study_type_weight=0.3,
        age_weight_0=0,
    )
    assert actual == RankingParams(
        window_size=DEFAULT_SEARCH_CONFIG.ranking_params.window_size,
        original_weight=DEFAULT_SEARCH_CONFIG.ranking_params.original_weight,
        reranking_weight=0.2,
        publish_year_default=1950,
        publish_year_origin=2020,
        publish_year_scale=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_scale,
        publish_year_offset=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_offset,
        publish_year_decay=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_decay,
        best_quartile_default=DEFAULT_SEARCH_CONFIG.ranking_params.best_quartile_default,
        best_quartile_weight=DEFAULT_SEARCH_CONFIG.ranking_params.best_quartile_weight,
        publish_year_weight=DEFAULT_SEARCH_CONFIG.ranking_params.publish_year_weight,
        study_type_weight=0.3,
        sjr_cite_weight=DEFAULT_SEARCH_CONFIG.ranking_params.sjr_cite_weight,
        cite_weight=DEFAULT_SEARCH_CONFIG.ranking_params.cite_weight,
        age_weight_0=0,
        age_weight_1=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_1,
        age_weight_2=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_2,
        age_weight_3=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_3,
        age_weight_4=DEFAULT_SEARCH_CONFIG.ranking_params.age_weight_4,
        kw_recall_weight=DEFAULT_SEARCH_CONFIG.ranking_params.kw_recall_weight,
        kw_boost_weight=DEFAULT_SEARCH_CONFIG.ranking_params.kw_boost_weight,
    )


def test_extract_phrases() -> None:
    original = '"simple phrase query"'
    expected = [
        "simple phrase query",
    ]
    actual = extract_phrases(original)
    assert actual == expected

    original = '"Self-Administered surveys" AND "region of origin" AND "purchase behaviour"'
    expected = [
        "Self-Administered surveys",
        "region of origin",
        "purchase behaviour",
    ]
    actual = extract_phrases(original)
    assert actual == expected

    original = '"microRNA-1246" "beta estradiol"'
    expected = [
        "microRNA-1246",
        "beta estradiol",
    ]
    actual = extract_phrases(original)
    assert actual == expected

    original = '"eosinophilic esophagitis" microRNA'
    expected = [
        "eosinophilic esophagitis",
    ]
    actual = extract_phrases(original)
    assert actual == expected

    original = 'test that an "unclosed quote is handled correctly'
    expected = []
    actual = extract_phrases(original)
    assert actual == expected

    original = "there are no quotes in this query"
    expected = []
    actual = extract_phrases(original)
    assert actual == expected

    original = 'attention is "all you need" except for "birds and cats" test " test'
    expected = [
        "all you need",
        "birds and cats",
    ]
    actual = extract_phrases(original)
    assert actual == expected

    ###############################
    # Failure modes
    ###############################
    # When open quote is preceded by other punctuation, NLTK doesn't recognize it as an open quote
    original = 'o microRNA-"4516" está relacionado com a menopausa?'
    expected = []
    actual = extract_phrases(original)
    assert actual == expected


def test_sort_vector_to_ranking_params() -> None:
    sort_vector = (
        "[125,1.0,1.0,1970,2023,0,0,0,3,0.15,0.05,0,0.02,0,0.7,0.4,0.27,0.23,0.18,0.05,0.25]"
    )
    actual = sort_vector_to_ranking_params(sort_vector)
    assert actual == DEFAULT_SEARCH_CONFIG.ranking_params

    sort_vector = (
        "[300,1.0,1.0,1970,2023,0,0,0,3,0.15,0.05,0,0.02,0,0.7,0.4,0.27,0.23,0.18,0.05,0.25]"
    )
    actual = sort_vector_to_ranking_params(sort_vector)
    assert actual == make_ranking_params(window_size=300)

    sort_vector = (
        "[125,0.5,1.0,1970,2023,0,0,0,4,0.15,0.05,0,0.02,0,0.7,0.4,0.27,0.23,0.18,0.05,0.25]"
    )
    actual = sort_vector_to_ranking_params(sort_vector)
    assert actual == make_ranking_params(original_weight=0.5, best_quartile_default=4)


def test_remove_punctuation() -> None:
    original = "what? is this a test, query!!?"
    cleaned = "what is this a test query"

    actual_keyword, actual_vector = remove_punctuation(
        keyword_text=original,
        vector_text=original,
        keyword_only=False,
    )
    assert actual_keyword == cleaned
    assert actual_vector == cleaned

    actual_keyword, actual_vector = remove_punctuation(
        keyword_text=original,
        vector_text=original,
        keyword_only=True,
    )
    assert actual_keyword == cleaned
    assert actual_vector == original


def test_remove_stopwords() -> None:
    original = "what? is this a test, query!!?"
    cleaned = "what? test, query!!?"

    actual_keyword, actual_vector = remove_stopwords(
        keyword_text=original,
        vector_text=original,
        keyword_only=False,
    )
    assert actual_keyword == cleaned
    assert actual_vector == cleaned

    actual_keyword, actual_vector = remove_stopwords(
        keyword_text=original,
        vector_text=original,
        keyword_only=True,
    )
    assert actual_keyword == cleaned
    assert actual_vector == original
