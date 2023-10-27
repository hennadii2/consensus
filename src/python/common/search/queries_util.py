"""
TODO(cvarano): It's simpler to duplicate the three util functions to support
both paper & claim search. This will be cleaned up after claim search is deprecated.
"""
from collections.abc import Mapping
from typing import Any, Optional

from common.search.document_types import HumanStudyKeywordEnum
from common.search.search_util import RankingParams, SearchFilter, extract_phrases


def _add_range_query(
    field_name: str, min_value: Optional[int], max_value: Optional[int]
) -> dict[str, Any]:
    range_query = {}
    if min_value is not None:
        range_query["gte"] = min_value
    if max_value is not None:
        range_query["lte"] = max_value
    return {"range": {field_name: range_query}}


def _make_filter_queries(
    search_filter: SearchFilter,
) -> list[dict[str, Any]]:
    filter_queries: list[dict[str, Any]] = []
    if search_filter.year_min is not None or search_filter.year_max is not None:
        filter_queries.append(
            _add_range_query("publish_year", search_filter.year_min, search_filter.year_max)
        )
    if search_filter.filter_controlled_studies:
        filter_queries.append({"term": {"is_controlled_study": True}})
    if search_filter.filter_animal_studies:
        filter_queries.append({"term": {"is_animal_study": True}})
    if search_filter.filter_human_studies:
        filter_queries.append({"term": {"population_type": HumanStudyKeywordEnum.HUMAN.value}})
    if search_filter.sample_size_min is not None or search_filter.sample_size_max is not None:
        filter_queries.append(
            _add_range_query(
                "sample_size", search_filter.sample_size_min, search_filter.sample_size_max
            )
        )
    if (
        search_filter.sjr_best_quartile_min is not None
        or search_filter.sjr_best_quartile_max is not None
    ):
        filter_queries.append(
            _add_range_query(
                "sjr_best_quartile",
                search_filter.sjr_best_quartile_min,
                search_filter.sjr_best_quartile_max,
            )
        )
    if search_filter.limit_to_fields_of_study:
        filter_queries.append(
            {
                "terms": {
                    "fields_of_study": [x.value for x in search_filter.limit_to_fields_of_study]
                }
            }
        )
    if len(search_filter.limit_to_study_types) > 0:
        filter_queries.append(
            {"terms": {"study_type": [x.value for x in search_filter.limit_to_study_types]}}
        )
    return filter_queries


def _make_phrase_query(
    phrase_text: str,
) -> Mapping[str, Any]:
    """
    Returns a match_phrase query for exact matches of the given phrase.
    """
    return {
        "match_phrase": {
            "search_text.exact": {
                "query": phrase_text,
            }
        }
    }


def make_keyword_search_query(
    text: str,
    search_filter: SearchFilter,
) -> Mapping[str, Any]:
    """
    Returns a keyword search query configured by the given parameters.
    """
    # Default matchset for recall
    or_query: dict[str, Any] = {
        "match": {
            "search_text": {
                "query": text,
            }
        }
    }
    # Gives a boost to claims that contain ALL terms
    and_query: dict[str, Any] = {
        "match": {
            "search_text": {
                "query": text,
                "operator": "and",
            }
        }
    }
    bool_query: dict[str, Any] = {
        "bool": {
            "should": [and_query, or_query],
        }
    }
    # If there are phrases, we restrict the match set to those that contain all phrases
    phrases = extract_phrases(text)
    if phrases:
        bool_query["bool"]["must"] = [_make_phrase_query(phrase) for phrase in phrases]
    # Filter background claims, if needed
    must_not_queries: list[dict[str, Any]] = []
    if len(search_filter.known_background_claim_ids) > 0:
        for background_claim_id in search_filter.known_background_claim_ids:
            must_not_queries.append({"match": {"claim_id": background_claim_id}})
    if must_not_queries:
        bool_query["bool"]["must_not"] = must_not_queries
    # Apply search filters
    filter_queries: list[dict[str, Any]] = _make_filter_queries(search_filter)
    if filter_queries:
        bool_query["bool"]["filter"] = filter_queries

    return bool_query


def make_similarity_search_rescore_query(
    query_embedding: list[Any],
    # Number of results to apply similarity search
    window_size: int,
    # Weight to apply to similiarity search results
    similarity_weight: float,
    # Weight to apply to claim embedding similiarity search. Applicable when using
    # multi vector search.
    claim_embedding_boost: Optional[float],
    # Weight to apply to title embedding. Applicaible when using multi vector search.
    title_embedding_boost: Optional[float],
) -> Mapping[str, Any]:
    """
    Returns a rescore based vector similarity search query configured by the given parameters.
    """

    if claim_embedding_boost is not None and title_embedding_boost is not None:
        script = {
            "source": """
          double value1 = dotProduct(params.query_embedding, 'embedding');
          double claim_score = params.claim_boost * sigmoid(1, Math.E, -value1);

          double value2 = dotProduct(params.query_embedding, 'title_embedding');
          double title_score = params.title_boost * sigmoid(1, Math.E, -value2);

          return claim_score + title_score;
                               """,
            "params": {
                "claim_boost": claim_embedding_boost,
                "title_boost": title_embedding_boost,
                "similarity_weight": similarity_weight,
                "query_embedding": query_embedding,
            },
        }
    else:
        script = {
            "source": """
          double value = dotProduct(params.query_embedding, 'embedding');
          return params.similarity_weight * sigmoid(1, Math.E, -value);
                  """,
            "params": {
                "similarity_weight": similarity_weight,
                "query_embedding": query_embedding,
            },
        }

    return {
        "window_size": window_size,
        "query": {
            "score_mode": "total",
            "rescore_query": {"function_score": {"script_score": {"script": script}}},
            "query_weight": 0.0,
            "rescore_query_weight": 1.0,
        },
    }


def make_sort_rescore_query(
    # Number of results to apply sorting
    window_size: int,
    # Weight to apply to claim probability in sort
    probability_weight: float,
    # Weight to apply to citation count in sort
    citation_count_weight: float,
    # Minimum and maximum bounds for normalizing citation count between [0, 1]
    citation_count_min: float,
    citation_count_max: float,
    # Weight to apply to publishing year in sort
    publish_year_weight: float,
    # Minimum and maximum bounds for normalizing publish year between [0, 1]
    publish_year_min: int,
    publish_year_max: int,
    # Weight to apply to SJR best quartile in sort
    best_quartile_weight: float,
    # Default value to use for SJR best quartile when not available
    # This value should be in the range [1, 4], where 1 is the highest score.
    best_quartile_default: float,
) -> Mapping[str, Any]:
    """
    Returns a rescore based results sort configured by the given parameters.
    """
    return {
        "window_size": window_size,
        "query": {
            "score_mode": "total",
            "rescore_query": {
                "function_score": {
                    "script_score": {
                        "script": {
                            "source": """
  double prob = params._source['probability'];
  double prob_score = (prob - 0.5) / (1.0 - 0.5);

  double cite = params._source['citation_count'];
  double cite_score = (cite - params.min_cite) / (params.max_cite - params.min_cite);
  cite_score = Math.max(0.0, Math.min(1.0, cite_score));

  double year = params._source['publish_year'];
  double year_score = (year - params.min_year) / (params.max_year - params.min_year);
  year_score = Math.max(0.0, Math.min(1.0, year_score));

  double best_quartile = field('sjr_best_quartile').get(0);
  if (best_quartile == 0) {
    best_quartile = params.best_quartile_default;
  }
  double best_quartile_score = (4.0 - best_quartile) / (4.0 - 1.0);
  best_quartile_score = Math.max(0.0, Math.min(1.0, best_quartile_score));

  return params.prob_weight * prob_score +
         params.cite_weight * cite_score +
         params.year_weight * year_score +
         params.best_quartile_weight * best_quartile_score;
                           """,
                            "params": {
                                "prob_weight": probability_weight,
                                "cite_weight": citation_count_weight,
                                "year_weight": publish_year_weight,
                                "min_year": publish_year_min,
                                "max_year": publish_year_max,
                                "min_cite": citation_count_min,
                                "max_cite": citation_count_max,
                                "best_quartile_weight": best_quartile_weight,
                                "best_quartile_default": best_quartile_default,
                            },
                        }
                    }
                }
            },
            "query_weight": 1.0,
            "rescore_query_weight": 1.0,
        },
    }


def make_elser_query(
    query_text: str,
    search_filter: SearchFilter,
    ranking_params: RankingParams,
) -> dict[str, Any]:
    # ELSER must use text_expansion query, and must have the specified model_id deployed
    elser_query = {
        "text_expansion": {"ml.tokens": {"model_id": ".elser_model_1", "model_text": query_text}}
    }
    # Default matchset for recall
    or_query: dict[str, Any] = {
        "match": {
            "search_text": {
                "query": query_text,
                "boost": ranking_params.kw_recall_weight,
            }
        }
    }
    # Gives a boost to claims that contain ALL terms
    and_query: dict[str, Any] = {
        "match": {
            "search_text": {
                "query": query_text,
                "operator": "and",
                "boost": ranking_params.kw_boost_weight,
            }
        }
    }
    bool_query: dict[str, Any] = {
        "bool": {
            "should": [elser_query, and_query, or_query],
        }
    }
    # If there are phrases, we restrict the match set to those that contain all phrases
    phrases = extract_phrases(query_text)
    if phrases:
        bool_query["bool"]["must"] = [_make_phrase_query(phrase) for phrase in phrases]
    filter_queries: list[dict[str, Any]] = _make_filter_queries(search_filter)
    if len(filter_queries):
        bool_query["bool"]["filter"] = filter_queries

    return bool_query


def make_reranking_query(
    ranking_params: RankingParams,
) -> Mapping[str, Any]:
    """
    Returns a rescore based results sort configured by the given parameters.

    It requires the following fields to be available (indexed or runtime):
    - ln_cite_smooth
    - paper_age
    - publish_year
    - sjr_best_quartile
    - is_quality_study_type
    """
    return {
        "window_size": ranking_params.window_size,
        "query": {
            "score_mode": "total",
            "rescore_query": {
                "function_score": {
                    "script_score": {
                        "script": {
                            "source": """
  long age = field('paper_age').get(0);
  double age_weight;
  if (age == 1) {
    age_weight = params.age0_wt;
  } else if (age == 2) {
    age_weight = params.age1_wt;
  } else if (age == 3) {
    age_weight = params.age2_wt;
  } else if (age >= 4 && age <= 10) {
    age_weight = params.age3_wt;
  } else if (age > 10) {
    age_weight = params.age4_wt;
  } else {
    age_weight = 0;
  }

  double year = field('publish_year').get(params.default_year);
  double year_score;
  if (params.year_decay == 0 || params.year_scale == 0) {
    year_score = (year - params.default_year) / (params.year_origin - params.default_year);
    year_score = Math.max(0.0, Math.min(1.0, year_score));
  } else {
    year_score = decayNumericExp(
                    params.year_origin,
                    params.year_scale,
                    params.year_offset,
                    params.year_decay,
                    year);
  }

  double best_quartile = field('sjr_best_quartile').get(0);
  if (best_quartile == 0) {
    best_quartile = params.best_quartile_default;
  }
  double sjr_score = (4.0 - best_quartile);
  double best_quartile_score = sjr_score / (4.0 - 1.0);
  best_quartile_score = Math.max(0.0, Math.min(1.0, best_quartile_score));

  double cite_score = field('ln_cite_smooth').get(0);
  double sjr_cite_score = sjr_score * cite_score;

  int study_type_score = field('is_quality_study_type').get(false) ? 1 : 0;

  return age_weight * cite_score +
         params.study_type_weight * study_type_score +
         params.cite_weight * cite_score +
         params.year_weight * year_score +
         params.best_quartile_weight * best_quartile_score +
         params.sjr_cite_weight * sjr_cite_score;
                           """,
                            "params": {
                                "age0_wt": ranking_params.age_weight_0,
                                "age1_wt": ranking_params.age_weight_1,
                                "age2_wt": ranking_params.age_weight_2,
                                "age3_wt": ranking_params.age_weight_3,
                                "age4_wt": ranking_params.age_weight_4,
                                "default_year": ranking_params.publish_year_default,
                                "year_origin": ranking_params.publish_year_origin,
                                "year_scale": ranking_params.publish_year_scale,
                                "year_offset": ranking_params.publish_year_offset,
                                "year_decay": ranking_params.publish_year_decay,
                                "year_weight": ranking_params.publish_year_weight,
                                "best_quartile_weight": ranking_params.best_quartile_weight,
                                "best_quartile_default": ranking_params.best_quartile_default,
                                "sjr_cite_weight": ranking_params.sjr_cite_weight,
                                "cite_weight": ranking_params.cite_weight,
                                "study_type_weight": ranking_params.study_type_weight,
                            },
                        }
                    }
                }
            },
            "query_weight": ranking_params.original_weight,
            "rescore_query_weight": ranking_params.reranking_weight,
        },
    }


def make_paper_keyword_search_query(
    query_text: str,
    search_filter: SearchFilter,
    debug_paper_id: Optional[str] = None,
) -> Mapping[str, Any]:
    """
    Returns a keyword search query configured by the given parameters.
    """
    # Default matchset for recall
    or_query: dict[str, Any] = {
        "match": {
            "search_text": {
                "query": query_text,
            }
        }
    }
    # Gives a boost to claims that contain ALL terms
    and_query: dict[str, Any] = {
        "match": {
            "search_text": {
                "query": query_text,
                "operator": "and",
            }
        }
    }
    bool_query: dict[str, Any] = {
        "bool": {
            "should": [and_query, or_query],
        }
    }
    # If there are phrases, we restrict the match set to those that contain all phrases
    phrases = extract_phrases(query_text)
    if phrases:
        bool_query["bool"]["must"] = [_make_phrase_query(phrase) for phrase in phrases]
    # Apply search filters
    filter_queries: list[dict[str, Any]] = _make_filter_queries(search_filter)
    # If debug_paper_id is provided, we filter to only that paper
    if debug_paper_id is not None:
        filter_queries.append({"term": {"paper_id": {"value": debug_paper_id}}})
    if filter_queries:
        bool_query["bool"]["filter"] = filter_queries

    return bool_query


def make_paper_similarity_search_rescore_query(
    query_embedding: list[Any],
    # Number of results to apply similarity search
    window_size: int,
    # Weight to apply to similiarity search results
    similarity_weight: float,
) -> Mapping[str, Any]:
    """
    Returns a rescore based vector similarity search query configured by the given parameters.
    """
    script = {
        "source": """
        double value = dotProduct(params.query_embedding, 'title_abstract_embedding');
        return params.similarity_weight * sigmoid(1, Math.E, -value);
                """,
        "params": {
            "similarity_weight": similarity_weight,
            "query_embedding": query_embedding,
        },
    }

    return {
        "window_size": window_size,
        "query": {
            "score_mode": "total",
            "rescore_query": {"function_score": {"script_score": {"script": script}}},
            "query_weight": 0.0,
            "rescore_query_weight": 1.0,
        },
    }


def make_paper_sort_rescore_query(
    # Number of results to apply sorting
    window_size: int,
    # Weight to apply to citation count in sort
    citation_count_weight: float,
    # Minimum and maximum bounds for normalizing citation count between [0, 1]
    citation_count_min: float,
    citation_count_max: float,
    # Weight to apply to publishing year in sort
    publish_year_weight: float,
    # Minimum and maximum bounds for normalizing publish year between [0, 1]
    publish_year_min: int,
    publish_year_max: int,
    # Weight to apply to SJR best quartile in sort
    best_quartile_weight: float,
    # Default value to use for SJR best quartile when not available
    # This value should be in the range [1, 4], where 1 is the highest score.
    best_quartile_default: float,
) -> Mapping[str, Any]:
    """
    Returns a rescore based results sort configured by the given parameters.
    """
    return {
        "window_size": window_size,
        "query": {
            "score_mode": "total",
            "rescore_query": {
                "function_score": {
                    "script_score": {
                        "script": {
                            "source": """
  double cite = field('citation_count').get(0);
  double cite_score = (cite - params.min_cite) / (params.max_cite - params.min_cite);
  cite_score = Math.max(0.0, Math.min(1.0, cite_score));

  double year = field('publish_year').get(0);
  double year_score = (year - params.min_year) / (params.max_year - params.min_year);
  year_score = Math.max(0.0, Math.min(1.0, year_score));

  double best_quartile = field('sjr_best_quartile').get(0);
  if (best_quartile == 0) {
    best_quartile = params.best_quartile_default;
  }
  double best_quartile_score = (4.0 - best_quartile) / (4.0 - 1.0);
  best_quartile_score = Math.max(0.0, Math.min(1.0, best_quartile_score));

  return params.cite_weight * cite_score +
         params.year_weight * year_score +
         params.best_quartile_weight * best_quartile_score;
                           """,
                            "params": {
                                "cite_weight": citation_count_weight,
                                "year_weight": publish_year_weight,
                                "min_year": publish_year_min,
                                "max_year": publish_year_max,
                                "min_cite": citation_count_min,
                                "max_cite": citation_count_max,
                                "best_quartile_weight": best_quartile_weight,
                                "best_quartile_default": best_quartile_default,
                            },
                        }
                    }
                }
            },
            "query_weight": 1.0,
            "rescore_query_weight": 1.0,
        },
    }
