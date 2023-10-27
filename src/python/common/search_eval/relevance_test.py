import functools

import pandas as pd
from common.search_eval.relevance import (
    _average_precision,
    _is_relevant,
    _ndcg,
    _precision_at_k,
    _recall_at_k,
    _reciprocal_rank,
    compute_metrics,
)

QUERY_COL = "query"
RANK_COL = "rank"
RELEVANCE_COL = "relevance"
GRADED_RELEVANCE_COL = "graded_relevance"

# TODO(cvarano): add tests with missing labels, missing ranks
DATA_NO_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_TOP1_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_TOP3_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [2, 2, 2, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_BOTTOM3_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 0, 0, 2, 2, 2],
    }
)
DATA_SPARSE_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 0, 2, 0, 0, 2, 0, 0, 2, 0],
    }
)
DATA_REVERSE_RANK = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [10, 9, 8, 7, 6, 5, 4, 3, 2, 1],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
    }
)
DATA_UNSORTED_RANK = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [3, 4, 1, 8, 10, 2, 7, 5, 9, 6],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 2, 0, 0, 0, 0],
    }
)
DATA_MISSING_LABELS = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [2, 0, 2, 0, 0, None, None, None, None, None],
    }
)
DATA_MISSING_LABELS_NONCONTIGUOUS = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [2, 0, None, 0, None, None, None, 2, None, 0],
    }
)
DATA_MISSING_RANKS = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, None, None, None, None, None],
        RELEVANCE_COL: [2, 0, 2, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_GRADED = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 5,
        RANK_COL: [1, 2, 3, 4, 5],
        GRADED_RELEVANCE_COL: [1, 2, 2, 0, 1],
    }
)
# Labels with 5-point scale
DATA_5PT_NO_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_5PT_TOP1_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [4, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_5PT_TOP3_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [3, 4, 3, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_5PT_BOTTOM3_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 0, 0, 3, 3, 4],
    }
)
DATA_5PT_SPARSE_RELEVANT = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 0, 4, 0, 0, 4, 0, 0, 3, 0],
    }
)
DATA_5PT_UNSORTED_RANK = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10,
        RANK_COL: [3, 4, 1, 8, 10, 2, 7, 5, 9, 6],
        RELEVANCE_COL: [0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
    }
)
DATA_5PT_GRADED_DESC = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 5,
        RANK_COL: [1, 2, 3, 4, 5],
        GRADED_RELEVANCE_COL: [4, 3, 2, 1, 0],
    }
)


precision_at_k_partial = functools.partial(
    _precision_at_k,
    rank_col=RANK_COL,
    relevance_col=RELEVANCE_COL,
)
recall_at_k_partial = functools.partial(
    _recall_at_k,
    rank_col=RANK_COL,
    relevance_col=RELEVANCE_COL,
)
average_precision_partial = functools.partial(
    _average_precision,
    rank_col=RANK_COL,
    relevance_col=RELEVANCE_COL,
)
reciprocal_rank_partial = functools.partial(
    _reciprocal_rank,
    rank_col=RANK_COL,
    relevance_col=RELEVANCE_COL,
)
ndcg_partial = functools.partial(
    _ndcg,
    rank_col=RANK_COL,
    relevance_col=GRADED_RELEVANCE_COL,
)
compute_metrics_partial = functools.partial(
    compute_metrics,
    query_col=QUERY_COL,
    rank_col=RANK_COL,
    relevance_col=RELEVANCE_COL,
)


def test_is_relevant() -> None:
    labels = pd.Series([0, 1, 2, 3, 4])
    paper_eval = True
    actual = _is_relevant(labels, paper_eval)
    assert actual.equals(pd.Series([False, False, False, True, True]))

    labels = pd.Series([0, 1, 2])
    paper_eval = False
    actual = _is_relevant(labels, paper_eval)
    assert actual.equals(pd.Series([False, False, True]))


def test_precision_at_k() -> None:
    # Test sorted datasets with k=10
    actual = precision_at_k_partial(DATA_NO_RELEVANT, k=10, paper_eval=False)
    assert actual == 0.0

    actual = precision_at_k_partial(DATA_TOP1_RELEVANT, k=10, paper_eval=False)
    assert actual == 0.1

    actual = precision_at_k_partial(DATA_TOP3_RELEVANT, k=10, paper_eval=False)
    assert actual == 0.3

    actual = precision_at_k_partial(DATA_BOTTOM3_RELEVANT, k=10, paper_eval=False)
    assert actual == 0.3

    actual = precision_at_k_partial(DATA_SPARSE_RELEVANT, k=10, paper_eval=False)
    assert actual == 0.3

    # Test sorted datasets with k=5
    actual = precision_at_k_partial(DATA_NO_RELEVANT, k=5, paper_eval=False)
    assert actual == 0.0

    actual = precision_at_k_partial(DATA_TOP1_RELEVANT, k=5, paper_eval=False)
    assert actual == 0.2

    actual = precision_at_k_partial(DATA_TOP3_RELEVANT, k=5, paper_eval=False)
    assert actual == 0.6

    actual = precision_at_k_partial(DATA_BOTTOM3_RELEVANT, k=5, paper_eval=False)
    assert actual == 0.0

    actual = precision_at_k_partial(DATA_SPARSE_RELEVANT, k=5, paper_eval=False)
    assert actual == 0.2

    # Test unsorted datasets with k=10
    actual = precision_at_k_partial(DATA_REVERSE_RANK, k=10, paper_eval=False)
    assert actual == 0.1

    actual = precision_at_k_partial(DATA_UNSORTED_RANK, k=10, paper_eval=False)
    assert actual == 0.1

    # Test unsorted datasets with k=5
    actual = precision_at_k_partial(DATA_REVERSE_RANK, k=5, paper_eval=False)
    assert actual == 0.2

    actual = precision_at_k_partial(DATA_UNSORTED_RANK, k=5, paper_eval=False)
    assert actual == 0.2

    # TODO(cvarano): continue here probably
    actual = precision_at_k_partial(DATA_MISSING_LABELS, k=10, paper_eval=False)
    assert actual == 0.2

    actual = precision_at_k_partial(DATA_MISSING_LABELS_NONCONTIGUOUS, k=10, paper_eval=False)
    assert actual == 0.2

    # 5-point scale
    actual = precision_at_k_partial(DATA_5PT_NO_RELEVANT, k=10, paper_eval=True)
    assert actual == 0.0

    actual = precision_at_k_partial(DATA_5PT_TOP1_RELEVANT, k=10, paper_eval=True)
    assert actual == 0.1

    actual = precision_at_k_partial(DATA_5PT_TOP3_RELEVANT, k=10, paper_eval=True)
    assert actual == 0.3

    actual = precision_at_k_partial(DATA_5PT_BOTTOM3_RELEVANT, k=10, paper_eval=True)
    assert actual == 0.3

    actual = precision_at_k_partial(DATA_5PT_SPARSE_RELEVANT, k=10, paper_eval=True)
    assert actual == 0.3


def test_recall_at_k() -> None:
    pass


def test_average_precision() -> None:
    # test sorted datasets with k=10
    actual = average_precision_partial(DATA_NO_RELEVANT, N=10, paper_eval=False)
    assert actual.iloc[0] == 0.0

    actual = average_precision_partial(DATA_TOP1_RELEVANT, N=10, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = average_precision_partial(DATA_TOP3_RELEVANT, N=10, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = average_precision_partial(DATA_BOTTOM3_RELEVANT, N=10, paper_eval=False)
    assert actual.iloc[0] == (1 / 8 + 2 / 9 + 3 / 10) / 3

    actual = average_precision_partial(DATA_SPARSE_RELEVANT, N=10, paper_eval=False)
    assert actual.iloc[0] == 1 / 3

    # test sorted datasets with k=5
    actual = average_precision_partial(DATA_NO_RELEVANT, N=5, paper_eval=False)
    assert actual.iloc[0] == 0.0

    actual = average_precision_partial(DATA_TOP1_RELEVANT, N=5, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = average_precision_partial(DATA_TOP3_RELEVANT, N=5, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = average_precision_partial(DATA_BOTTOM3_RELEVANT, N=5, paper_eval=False)
    assert actual.iloc[0] == 0.0

    actual = average_precision_partial(DATA_SPARSE_RELEVANT, N=5, paper_eval=False)
    assert actual.iloc[0] == 1 / 3

    # test unsorted datasets with k=10
    actual = average_precision_partial(DATA_REVERSE_RANK, N=10, paper_eval=False)
    assert actual.iloc[0] == 0.5

    actual = average_precision_partial(DATA_UNSORTED_RANK, N=10, paper_eval=False)
    assert actual.iloc[0] == 0.5

    # test unsorted datasets with k=5
    actual = average_precision_partial(DATA_REVERSE_RANK, N=5, paper_eval=False)
    assert actual.iloc[0] == 0.5

    actual = average_precision_partial(DATA_UNSORTED_RANK, N=5, paper_eval=False)
    assert actual.iloc[0] == 0.5

    # 5-point scale
    actual = average_precision_partial(DATA_5PT_NO_RELEVANT, N=10, paper_eval=True)
    assert actual.iloc[0] == 0.0

    actual = average_precision_partial(DATA_5PT_TOP1_RELEVANT, N=10, paper_eval=True)
    assert actual.iloc[0] == 1.0

    actual = average_precision_partial(DATA_5PT_TOP3_RELEVANT, N=10, paper_eval=True)
    assert actual.iloc[0] == 1.0

    actual = average_precision_partial(DATA_5PT_BOTTOM3_RELEVANT, N=10, paper_eval=True)
    assert actual.iloc[0] == (1 / 8 + 2 / 9 + 3 / 10) / 3

    actual = average_precision_partial(DATA_5PT_SPARSE_RELEVANT, N=10, paper_eval=True)
    assert actual.iloc[0] == 1 / 3


def test_reciprocal_rank() -> None:
    # test sorted datasets with k=10
    actual = reciprocal_rank_partial(DATA_NO_RELEVANT, k=10, paper_eval=False)
    assert actual.iloc[0] == 0.0

    actual = reciprocal_rank_partial(DATA_TOP1_RELEVANT, k=10, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = reciprocal_rank_partial(DATA_TOP3_RELEVANT, k=10, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = reciprocal_rank_partial(DATA_BOTTOM3_RELEVANT, k=10, paper_eval=False)
    assert actual.iloc[0] == 1 / 8

    actual = reciprocal_rank_partial(DATA_SPARSE_RELEVANT, k=10, paper_eval=False)
    assert actual.iloc[0] == 1 / 3

    # test sorted datasets with k=5
    actual = reciprocal_rank_partial(DATA_NO_RELEVANT, k=5, paper_eval=False)
    assert actual.iloc[0] == 0.0

    actual = reciprocal_rank_partial(DATA_TOP1_RELEVANT, k=5, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = reciprocal_rank_partial(DATA_TOP3_RELEVANT, k=5, paper_eval=False)
    assert actual.iloc[0] == 1.0

    actual = reciprocal_rank_partial(DATA_BOTTOM3_RELEVANT, k=5, paper_eval=False)
    assert actual.iloc[0] == 0.0

    actual = reciprocal_rank_partial(DATA_SPARSE_RELEVANT, k=5, paper_eval=False)
    assert actual.iloc[0] == 1 / 3

    # test unsorted datasets with k=10
    actual = reciprocal_rank_partial(DATA_REVERSE_RANK, k=10, paper_eval=False)
    assert actual.iloc[0] == 0.5

    actual = reciprocal_rank_partial(DATA_UNSORTED_RANK, k=10, paper_eval=False)
    assert actual.iloc[0] == 0.5

    # test unsorted datasets with k=5
    actual = reciprocal_rank_partial(DATA_REVERSE_RANK, k=5, paper_eval=False)
    assert actual.iloc[0] == 0.5

    actual = reciprocal_rank_partial(DATA_UNSORTED_RANK, k=5, paper_eval=False)
    assert actual.iloc[0] == 0.5

    # 5-point scale
    actual = reciprocal_rank_partial(DATA_5PT_NO_RELEVANT, k=10, paper_eval=True)
    assert actual.iloc[0] == 0.0

    actual = reciprocal_rank_partial(DATA_5PT_TOP1_RELEVANT, k=10, paper_eval=True)
    assert actual.iloc[0] == 1.0

    actual = reciprocal_rank_partial(DATA_5PT_TOP3_RELEVANT, k=10, paper_eval=True)
    assert actual.iloc[0] == 1.0

    actual = reciprocal_rank_partial(DATA_5PT_BOTTOM3_RELEVANT, k=10, paper_eval=True)
    assert actual.iloc[0] == 1 / 8

    actual = reciprocal_rank_partial(DATA_5PT_SPARSE_RELEVANT, k=10, paper_eval=True)
    assert actual.iloc[0] == 1 / 3


def test_ndcg() -> None:
    actual = _ndcg(DATA_GRADED, rank_col=RANK_COL, relevance_col=GRADED_RELEVANCE_COL, k=5)
    assert actual.iloc[0] == 0.8207555803845797

    actual = _ndcg(
        DATA_5PT_GRADED_DESC, rank_col=RANK_COL, relevance_col=GRADED_RELEVANCE_COL, k=5
    )
    assert actual.iloc[0] == 1.0


DATA_MULTI_QUERY = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10 + ["test_query2"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 2, 0, 0, 0, 0, 0, 0, 2, 0] + [2, 0, 2, 0, 0, 0, 0, 0, 0, 0],
    }
)
DATA_5PT_MULTI_QUERY = pd.DataFrame(
    {
        QUERY_COL: ["test_query"] * 10 + ["test_query2"] * 10,
        RANK_COL: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] + [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        RELEVANCE_COL: [0, 4, 0, 0, 0, 0, 0, 0, 3, 0] + [3, 0, 4, 0, 0, 0, 0, 0, 0, 0],
    }
)


def test_compute_metrics() -> None:
    k = 10
    actual = compute_metrics_partial(DATA_NO_RELEVANT, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.0
    assert actual["average_precision"].iloc[0] == 0.0
    assert actual["reciprocal_rank"].iloc[0] == 0.0

    actual = compute_metrics_partial(DATA_TOP1_RELEVANT, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.1
    assert actual["average_precision"].iloc[0] == 1.0
    assert actual["reciprocal_rank"].iloc[0] == 1.0

    actual = compute_metrics_partial(DATA_UNSORTED_RANK, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.1
    assert actual["average_precision"].iloc[0] == 0.5
    assert actual["reciprocal_rank"].iloc[0] == 0.5

    actual = compute_metrics_partial(DATA_MULTI_QUERY, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.2
    assert actual["average_precision"].iloc[0] == (1 / 2 + 2 / 9) / 2
    assert actual["reciprocal_rank"].iloc[0] == 0.5
    assert actual[f"prec@{k}"].iloc[1] == 0.2
    assert actual["average_precision"].iloc[1] == (1 + 2 / 3) / 2
    assert actual["reciprocal_rank"].iloc[1] == 1.0

    k = 5
    actual = compute_metrics_partial(DATA_NO_RELEVANT, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.0
    assert actual["average_precision"].iloc[0] == 0.0
    assert actual["reciprocal_rank"].iloc[0] == 0.0

    actual = compute_metrics_partial(DATA_TOP1_RELEVANT, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.2
    assert actual["average_precision"].iloc[0] == 1.0
    assert actual["reciprocal_rank"].iloc[0] == 1.0

    actual = compute_metrics_partial(DATA_UNSORTED_RANK, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.2
    assert actual["average_precision"].iloc[0] == 0.5
    assert actual["reciprocal_rank"].iloc[0] == 0.5

    actual = compute_metrics_partial(DATA_MULTI_QUERY, k=k, paper_eval=False)
    assert actual[f"prec@{k}"].iloc[0] == 0.2
    assert actual["average_precision"].iloc[0] == 0.5
    assert actual["reciprocal_rank"].iloc[0] == 0.5
    assert actual[f"prec@{k}"].iloc[1] == 0.4
    assert actual["average_precision"].iloc[1] == (1 + 2 / 3) / 2
    assert actual["reciprocal_rank"].iloc[1] == 1.0

    k = 10
    actual = compute_metrics_partial(DATA_5PT_NO_RELEVANT, k=k, paper_eval=True)
    assert actual[f"prec@{k}"].iloc[0] == 0.0
    assert actual["average_precision"].iloc[0] == 0.0
    assert actual["reciprocal_rank"].iloc[0] == 0.0

    actual = compute_metrics_partial(DATA_5PT_TOP1_RELEVANT, k=k, paper_eval=True)
    assert actual[f"prec@{k}"].iloc[0] == 0.1
    assert actual["average_precision"].iloc[0] == 1.0
    assert actual["reciprocal_rank"].iloc[0] == 1.0

    actual = compute_metrics_partial(DATA_5PT_UNSORTED_RANK, k=k, paper_eval=True)
    assert actual[f"prec@{k}"].iloc[0] == 0.1
    assert actual["average_precision"].iloc[0] == 0.5
    assert actual["reciprocal_rank"].iloc[0] == 0.5

    actual = compute_metrics_partial(DATA_5PT_MULTI_QUERY, k=k, paper_eval=True)
    assert actual[f"prec@{k}"].iloc[0] == 0.2
    assert actual["average_precision"].iloc[0] == (1 / 2 + 2 / 9) / 2
    assert actual["reciprocal_rank"].iloc[0] == 0.5
    assert actual[f"prec@{k}"].iloc[1] == 0.2
    assert actual["average_precision"].iloc[1] == (1 + 2 / 3) / 2
    assert actual["reciprocal_rank"].iloc[1] == 1.0
