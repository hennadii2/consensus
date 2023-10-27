from typing import Dict, List, Optional

import numpy as np
import pandas as pd
from common.search_eval.constants import QUERY_COL, RANK_COL, RELEVANCE_COL
from loguru import logger


# graded claim labels are [2, 1, 0], where 2 is relevant
# graded paper labels are [4, 3, 2, 1, 0], where >=3 is relevant
def _is_relevant(labels: pd.Series, paper_eval: bool) -> pd.Series:
    return (labels >= 3) if paper_eval else (labels == 2)


def _precision_at_k(
    query_data: pd.DataFrame, k: int, rank_col: str, relevance_col: str, paper_eval: bool
) -> float:
    return (
        len(
            query_data[
                (query_data[rank_col] <= k) & (_is_relevant(query_data[relevance_col], paper_eval))
            ]
        )
        / k
    )


def _recall_at_k(
    query_data: pd.DataFrame, k: int, rank_col: str, relevance_col: str, paper_eval: bool
) -> pd.Series:
    total_relevant = query_data[_is_relevant(query_data[relevance_col], paper_eval)].shape[0]
    retrieved_relevant = query_data[
        (query_data[rank_col] <= k) & (_is_relevant(query_data[relevance_col], paper_eval))
    ].shape[0]
    recall = retrieved_relevant / total_relevant if total_relevant > 0 else 0
    return pd.Series(recall, index=["recall"])


# TODO(cvarano): parameterize prec/rec columns
def f1(df: pd.DataFrame, k: int) -> pd.DataFrame:
    """Add f1 column to dataframe."""
    df["f1"] = 2 * (df[f"prec@{k}"] * df["recall"]) / (df[f"prec@{k}"] + df["recall"])
    return df


def _average_precision(
    query_data: pd.DataFrame, N: int, rank_col: str, relevance_col: str, paper_eval: bool
) -> pd.Series:
    query_data = query_data[query_data[rank_col] <= N]
    query_data.sort_values(by=rank_col, inplace=True)
    total = 0.0
    for i in range(1, len(query_data) + 1):
        total += (
            0
            # if (query_data.iloc[i - 1][relevance_col] != 1)
            if (
                ~_is_relevant(query_data[relevance_col], paper_eval).iloc[i - 1]
            )  # TODO(cvarano): check this
            else _precision_at_k(query_data, i, rank_col, relevance_col, paper_eval=paper_eval)
        )
    num_rel = query_data[_is_relevant(query_data[relevance_col], paper_eval)].shape[0]
    return pd.Series(total / num_rel if num_rel > 0 else 0, index=["average_precision"])


def _reciprocal_rank(
    query_data: pd.DataFrame, k: int, rank_col: str, relevance_col: str, paper_eval: bool
) -> pd.Series:
    query_data = query_data[
        (query_data[rank_col] <= k) & (_is_relevant(query_data[relevance_col], paper_eval))
    ]
    query_data.sort_values(by=rank_col, inplace=True)
    if not len(query_data):
        return pd.Series(0.0, index=["reciprocal_rank"])
    return pd.Series(1.0 / float(query_data.iloc[0][rank_col]), index=["reciprocal_rank"])


def _ndcg(
    query_data: pd.DataFrame, k: int, rank_col: str, relevance_col: str, method: str = "exp"
) -> pd.Series:
    numerator_func = (lambda x: 2**x - 1) if method == "exp" else (lambda x: x)
    query_data = query_data[query_data[rank_col] <= k]

    def dcg_helper(qg):
        total = 0.0
        for i, rel in enumerate(qg[relevance_col]):
            total += numerator_func(rel) / np.log2(i + 2)
        return total

    query_data = query_data.sort_values(by=rank_col, ignore_index=True)
    dcg = dcg_helper(query_data)
    idcg = dcg_helper(
        query_data.sort_values(by=relevance_col, ascending=False, ignore_index=True, kind="stable")
    )
    ndcg = float(dcg / idcg) if idcg > 0.0 else 0.0
    return pd.Series(ndcg, index=["ndcg"])


def _validate_feature_metrics_dict(
    labelled_results: pd.DataFrame,
    feature_metrics_dict: Optional[Dict[str, List[str]]] = None,
) -> Optional[Dict[str, List[str]]]:
    if not feature_metrics_dict:
        return None

    for feature_name in list(feature_metrics_dict.keys()):
        if feature_name not in labelled_results.columns:
            logger.warning(f'Feature "{feature_name}" not in dataframe')
            del feature_metrics_dict[feature_name]

    return feature_metrics_dict


# TODO(cvarano): allow k to be a list of values
def compute_metrics(
    labelled_results: pd.DataFrame,
    k: int,
    query_col: str = QUERY_COL,
    rank_col: str = RANK_COL,
    relevance_col: str = RELEVANCE_COL,
    feature_metrics_dict: Optional[Dict[str, List[str]]] = None,
    paper_eval: bool = False,
) -> pd.DataFrame:
    labelled_results.sort_values(by=[query_col, rank_col], ignore_index=True)
    metrics_df = labelled_results.groupby(query_col, as_index=False).apply(
        lambda query_group: pd.Series(
            _precision_at_k(
                query_group,
                k=k,
                rank_col=rank_col,
                relevance_col=relevance_col,
                paper_eval=paper_eval,
            ),
            index=[f"prec@{k}"],
        )
    )
    recall_df = labelled_results.groupby(query_col, as_index=False).apply(
        lambda x: _recall_at_k(
            x, k=k, rank_col=rank_col, relevance_col=relevance_col, paper_eval=paper_eval
        )
    )
    metrics_df = metrics_df.merge(recall_df, on=query_col)
    metrics_df = f1(metrics_df, k=k)

    avg_prec_df = labelled_results.groupby(query_col, as_index=False).apply(
        lambda x: _average_precision(
            x, N=k, rank_col=rank_col, relevance_col=relevance_col, paper_eval=paper_eval
        )
    )
    metrics_df = metrics_df.merge(avg_prec_df, on=query_col)

    rr_df = labelled_results.groupby(query_col, as_index=False).apply(
        lambda x: _reciprocal_rank(
            x, k=k, rank_col=rank_col, relevance_col=relevance_col, paper_eval=paper_eval
        )
    )
    metrics_df = metrics_df.merge(rr_df, on=query_col)

    ndcg_df = labelled_results.groupby(query_col, as_index=False).apply(
        lambda x: _ndcg(x, k=k, rank_col=rank_col, relevance_col=relevance_col)
    )
    metrics_df = metrics_df.merge(ndcg_df, on=query_col)

    feature_metrics_dict = _validate_feature_metrics_dict(labelled_results, feature_metrics_dict)
    if feature_metrics_dict:
        feature_metrics_df = labelled_results.groupby(query_col, as_index=False).agg(
            feature_metrics_dict
        )
        feature_metrics_df.columns = pd.Index(
            ["_".join(col).strip("_") for col in feature_metrics_df.columns]
        )
        metrics_df = metrics_df.merge(feature_metrics_df, on=query_col)

    return metrics_df
