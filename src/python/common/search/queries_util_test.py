from common.search.document_types import FieldOfStudyKeywordEnum, StudyTypeKeywordEnum
from common.search.queries_util import (
    _add_range_query,
    _make_filter_queries,
    _make_phrase_query,
    make_elser_query,
    make_keyword_search_query,
    make_paper_keyword_search_query,
)
from common.search.search_util import make_ranking_params, make_search_filter


def test_add_range_query() -> None:
    actual = _add_range_query("sample_size", 50, None)
    assert actual == {
        "range": {
            "sample_size": {"gte": 50},
        }
    }

    actual = _add_range_query("sample_size", None, 100)
    assert actual == {
        "range": {
            "sample_size": {"lte": 100},
        }
    }

    actual = _add_range_query("sample_size", 50, 100)
    assert actual == {
        "range": {
            "sample_size": {"gte": 50, "lte": 100},
        }
    }

    actual = _add_range_query("publish_year", 2000, 2010)
    assert actual == {
        "range": {
            "publish_year": {"gte": 2000, "lte": 2010},
        }
    }


def test_make_filter_queries() -> None:
    search_filter = make_search_filter()
    actual = _make_filter_queries(search_filter)
    assert actual == []

    search_filter = make_search_filter(
        year_min=2000,
        year_max=2010,
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "range": {
                "publish_year": {"gte": 2000, "lte": 2010},
            }
        }
    ]

    search_filter = make_search_filter(
        year_min=2000,
        year_max=2010,
        sample_size_min=50,
        sample_size_max=100,
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "range": {
                "publish_year": {"gte": 2000, "lte": 2010},
            }
        },
        {
            "range": {
                "sample_size": {"gte": 50, "lte": 100},
            }
        },
    ]

    search_filter = make_search_filter(
        year_min=2000,
        year_max=2010,
        sample_size_min=50,
        sample_size_max=100,
        sjr_best_quartile_min=1,
        sjr_best_quartile_max=2,
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "range": {
                "publish_year": {"gte": 2000, "lte": 2010},
            }
        },
        {
            "range": {
                "sample_size": {"gte": 50, "lte": 100},
            }
        },
        {
            "range": {
                "sjr_best_quartile": {"gte": 1, "lte": 2},
            }
        },
    ]

    search_filter = make_search_filter(
        year_min=2000,
        year_max=2010,
        filter_controlled_studies=True,
        filter_human_studies=True,
        filter_animal_studies=True,
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "range": {
                "publish_year": {"gte": 2000, "lte": 2010},
            }
        },
        {
            "term": {
                "is_controlled_study": True,
            }
        },
        {
            "term": {
                "is_animal_study": True,
            }
        },
        {
            "term": {
                "population_type": "human",
            }
        },
    ]

    search_filter = make_search_filter(
        limit_to_fields_of_study=[
            FieldOfStudyKeywordEnum.MATHEMATICS,
            FieldOfStudyKeywordEnum.ENGINEERING,
        ],
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "terms": {
                "fields_of_study": ["Mathematics", "Engineering"],
            }
        },
    ]

    search_filter = make_search_filter(
        limit_to_study_types=[
            StudyTypeKeywordEnum.OTHER,
            StudyTypeKeywordEnum.RCT,
        ],
        limit_to_fields_of_study=[
            FieldOfStudyKeywordEnum.MATHEMATICS,
            FieldOfStudyKeywordEnum.ENGINEERING,
        ],
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "terms": {
                "fields_of_study": ["Mathematics", "Engineering"],
            }
        },
        {
            "terms": {
                "study_type": ["other", "rct"],
            }
        },
    ]

    search_filter = make_search_filter(
        year_min=2000,
        limit_to_study_types=[
            StudyTypeKeywordEnum.OTHER,
            StudyTypeKeywordEnum.RCT,
        ],
    )
    actual = _make_filter_queries(search_filter)
    assert actual == [
        {
            "range": {
                "publish_year": {"gte": 2000},
            }
        },
        {
            "terms": {
                "study_type": ["other", "rct"],
            }
        },
    ]


def test_make_phrase_query() -> None:
    actual = _make_phrase_query("test query")
    assert actual == {
        "match_phrase": {
            "search_text.exact": {
                "query": "test query",
            }
        }
    }


def test_make_keyword_search_query() -> None:
    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ]
        }
    }


def test_make_keyword_search_query_with_phrase_matching() -> None:
    actual = make_keyword_search_query(
        text='test query with an "unclosed quote',
        search_filter=make_search_filter(),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": 'test query with an "unclosed quote',
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": 'test query with an "unclosed quote',
                        }
                    }
                },
            ],
        }
    }

    actual = make_keyword_search_query(
        text='test query with "test phrase 1"',
        search_filter=make_search_filter(),
    )
    assert actual == {
        "bool": {
            "must": [
                {
                    "match_phrase": {
                        "search_text.exact": {
                            "query": "test phrase 1",
                        }
                    }
                },
            ],
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": 'test query with "test phrase 1"',
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": 'test query with "test phrase 1"',
                        }
                    }
                },
            ],
        }
    }

    actual = make_keyword_search_query(
        text='test query with "test phrase 1" and "test phrase 2"',
        search_filter=make_search_filter(),
    )
    assert actual == {
        "bool": {
            "must": [
                {
                    "match_phrase": {
                        "search_text.exact": {
                            "query": "test phrase 1",
                        }
                    },
                },
                {
                    "match_phrase": {
                        "search_text.exact": {
                            "query": "test phrase 2",
                        }
                    },
                },
            ],
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": 'test query with "test phrase 1" and "test phrase 2"',
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": 'test query with "test phrase 1" and "test phrase 2"',
                        }
                    }
                },
            ],
        }
    }


def test_make_keyword_search_query_range_filters() -> None:
    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(year_min=2010),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010},
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(year_max=2019, sample_size_min=100),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"lte": 2019},
                    },
                },
                {
                    "range": {
                        "sample_size": {"gte": 100},
                    },
                },
            ],
        },
    }


def test_make_keyword_search_query_known_background_claim_ids() -> None:
    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            known_background_claim_ids=["background_claim_id_1"],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "must_not": [{"match": {"claim_id": "background_claim_id_1"}}],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            known_background_claim_ids=[
                "background_claim_id_1",
                "background_claim_id_2",
                "background_claim_id_3",
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "must_not": [
                {"match": {"claim_id": "background_claim_id_1"}},
                {"match": {"claim_id": "background_claim_id_2"}},
                {"match": {"claim_id": "background_claim_id_3"}},
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            known_background_claim_ids=[
                "background_claim_id_1",
                "background_claim_id_2",
                "background_claim_id_3",
            ],
            sample_size_min=100,
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "range": {
                        "sample_size": {"gte": 100},
                    },
                }
            ],
            "must_not": [
                {"match": {"claim_id": "background_claim_id_1"}},
                {"match": {"claim_id": "background_claim_id_2"}},
                {"match": {"claim_id": "background_claim_id_3"}},
            ],
        },
    }


def test_make_keyword_search_query_limit_to_study_types() -> None:
    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            known_background_claim_ids=[
                "background_claim_id_1",
                "background_claim_id_2",
                "background_claim_id_3",
            ],
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "must_not": [
                {"match": {"claim_id": "background_claim_id_1"}},
                {"match": {"claim_id": "background_claim_id_2"}},
                {"match": {"claim_id": "background_claim_id_3"}},
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT]
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        },
    }


def test_make_keyword_search_query_limit_to_fields_of_study() -> None:
    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            known_background_claim_ids=[
                "background_claim_id_1",
                "background_claim_id_2",
                "background_claim_id_3",
            ],
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "must_not": [
                {"match": {"claim_id": "background_claim_id_1"}},
                {"match": {"claim_id": "background_claim_id_2"}},
                {"match": {"claim_id": "background_claim_id_3"}},
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
            ],
        },
    }

    actual = make_keyword_search_query(
        text="test query",
        search_filter=make_search_filter(
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    }
                },
            ],
            "filter": [
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
            ],
        },
    }


def test_make_elser_query() -> None:
    # Test baseline
    actual = make_elser_query(
        query_text="test query",
        search_filter=make_search_filter(),
        ranking_params=make_ranking_params(
            kw_recall_weight=0.5,
            kw_boost_weight=1.0,
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "text_expansion": {
                        "ml.tokens": {
                            "model_id": ".elser_model_1",
                            "model_text": "test query",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                            "boost": 1.0,
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "boost": 0.5,
                        }
                    },
                },
            ]
        }
    }

    # Test phrase matching
    actual = make_elser_query(
        query_text='"test" and "query"',
        search_filter=make_search_filter(),
        ranking_params=make_ranking_params(),
    )
    assert actual == {
        "bool": {
            "must": [
                {
                    "match_phrase": {
                        "search_text.exact": {
                            "query": "test",
                        }
                    }
                },
                {
                    "match_phrase": {
                        "search_text.exact": {
                            "query": "query",
                        }
                    }
                },
            ],
            "should": [
                {
                    "text_expansion": {
                        "ml.tokens": {
                            "model_id": ".elser_model_1",
                            "model_text": '"test" and "query"',
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": '"test" and "query"',
                            "operator": "and",
                            "boost": 0.25,
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": '"test" and "query"',
                            "boost": 0.05,
                        }
                    },
                },
            ],
        }
    }

    # Test range filters
    actual = make_elser_query(
        query_text="test query",
        search_filter=make_search_filter(year_min=2010, sample_size_max=100),
        ranking_params=make_ranking_params(),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "text_expansion": {
                        "ml.tokens": {
                            "model_id": ".elser_model_1",
                            "model_text": "test query",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                            "boost": 0.25,
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "boost": 0.05,
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010},
                    },
                },
                {
                    "range": {
                        "sample_size": {"lte": 100},
                    },
                },
            ],
        }
    }

    # Test string filters
    actual = make_elser_query(
        query_text="test query",
        search_filter=make_search_filter(
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT],
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
        ranking_params=make_ranking_params(),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "text_expansion": {
                        "ml.tokens": {
                            "model_id": ".elser_model_1",
                            "model_text": "test query",
                        }
                    }
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                            "boost": 0.25,
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "boost": 0.05,
                        }
                    },
                },
            ],
            "filter": [
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        }
    }


# TODO(cvarano): Cleanup after claim search is deprecated
def test_make_paper_keyword_search_query() -> None:
    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
        }
    }

    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(),
        debug_paper_id="paper_id_1",
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [{"term": {"paper_id": {"value": "paper_id_1"}}}],
        }
    }


def test_make_paper_keyword_search_query_range_filters() -> None:
    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(year_min=2010),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010},
                    },
                },
            ],
        },
    }

    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(sample_size_max=100),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "sample_size": {"lte": 100},
                    },
                },
            ],
        },
    }


def test_make_paper_keyword_search_query_limit_to_study_types() -> None:
    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        },
    }

    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        },
    }

    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(
            limit_to_study_types=[StudyTypeKeywordEnum.OTHER, StudyTypeKeywordEnum.RCT]
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "terms": {
                        "study_type": ["other", "rct"],
                    },
                },
            ],
        },
    }


def test_make_paper_keyword_search_query_limit_to_fields_of_study() -> None:
    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
            ],
        },
    }

    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(
            year_min=2010,
            year_max=2019,
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "range": {
                        "publish_year": {"gte": 2010, "lte": 2019},
                    },
                },
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
            ],
        },
    }

    actual = make_paper_keyword_search_query(
        query_text="test query",
        search_filter=make_search_filter(
            limit_to_fields_of_study=[
                FieldOfStudyKeywordEnum.MATHEMATICS,
                FieldOfStudyKeywordEnum.ENGINEERING,
            ],
        ),
    )
    assert actual == {
        "bool": {
            "should": [
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                            "operator": "and",
                        }
                    },
                },
                {
                    "match": {
                        "search_text": {
                            "query": "test query",
                        }
                    },
                },
            ],
            "filter": [
                {
                    "terms": {
                        "fields_of_study": ["Mathematics", "Engineering"],
                    },
                },
            ],
        },
    }
