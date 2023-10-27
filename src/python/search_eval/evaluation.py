import argparse
import os
from typing import Any, List, Optional, Tuple

import common.search_eval.config_util as config_util
import common.storage.gcs_util as gcs_util
import pandas as pd
from common.db.connect import DbEnv, MainDbClient
from common.db.papers import Papers
from common.models.similarity_search_embedding import (
    SimilaritySearchEmbeddingModel,
    initialize_similarity_search_embedding_model,
)
from common.search.claim_index import ClaimIndex
from common.search.connect import ElasticClient, SearchEnv
from common.search.paper_index import PaperIndex
from common.search.search_util import SearchFilter, SortParams, make_search_filter
from common.search_eval import eval_util, relevance
from common.search_eval.constants import (
    QUERY_COL,
    RANK_COL,
    RELEVANCE_COL,
    RELEVANCE_FEATURES,
    SCORE_COL,
)
from common.storage.connect import StorageEnv, init_storage_client
from google.cloud import storage
from loguru import logger
from web.backend.app.common.util import dedup_by_first_unique

EMBEDDING_MODEL = initialize_similarity_search_embedding_model()

CONFIG_DEFAULTS = {
    "db_env": "prod",
    "search_env": "dev",
    "page_size": 20,
    "k": 20,
    "paper_eval": False,
    "quantize_vectors": False,
    "use_vector_sim": True,
    "use_rescore": True,
}


# TODO(cvarano): add validation
def _override_yaml_config_with_cli_args(config: dict, args) -> dict:
    """
    Override config values with command line arguments. Arguments that are not
    provided are left unchanged. The original config is not retained.

    Args:
        config: dict of config values
    Returns:
        dict of config values with command line arguments applied
    """
    # Overrideable arguments
    if args.page_size is not None:
        config["page_size"] = args.page_size
    if args.k is not None:
        config["k"] = args.k
    if args.eval_suffix is not None:
        config["eval_suffix"] = args.eval_suffix
    else:
        config["eval_suffix"] = f"_{args.tag.replace('-', '_')}"

    # Command line-only arguments
    config["description"] = args.eval_description
    config["force_metrics"] = args.force_metrics
    config["num_queries"] = args.num_queries
    # Global defaults
    for k, v in CONFIG_DEFAULTS.items():
        if k not in config:
            config[k] = v
            logger.info(f"Using default value for {k}: {v}")

    return config


def _positive_integer(value: str) -> int:
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


def _parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config",
        "-c",
        default="src/python/search_eval/config.yaml",
        type=str,
        help="Path to yaml config file",
    )
    parser.add_argument(
        "--tag",
        "-t",
        default="default",
        type=str,
        help="Tag to use from the yaml config file",
    )
    parser.add_argument(
        "--force_metrics",
        action="store_true",
        help="Force evaluation metrics to be computed even when there are unlabelled annotations",
    )
    parser.add_argument(
        "--num_queries",
        "-n",
        default=50,
        type=_positive_integer,
        help="Number of test queries to evaluate",
    )
    parser.add_argument(
        "--page_size",
        "-s",
        default=None,
        type=_positive_integer,
        help="Number of results to return from search request",
    )
    parser.add_argument(
        "-k",
        default=None,
        type=_positive_integer,
        help="k to use for computing top-k metrics",
    )
    parser.add_argument(
        "--eval_suffix",
        default=None,
        help="Suffix to append to evaluation results file; defaults to tag name",
    )
    parser.add_argument(
        "--eval_description",
        required=True,
        help="Description of evaluation run, uploaded to eval directory for reference",
    )
    return parser.parse_args(argv)


def _label_search_results(
    storage_client: storage.Client,
    query_results: pd.DataFrame,
    paper_eval: bool,
) -> pd.DataFrame:
    if paper_eval:
        labels = eval_util.read_annotated_labels(storage_client, paper_eval=paper_eval)
    else:
        centaur = eval_util.get_centaur_labels()
        annotations = eval_util.read_annotated_labels(storage_client, paper_eval=paper_eval)
        labels = pd.concat([centaur, annotations], ignore_index=True)
    labelled_results = eval_util.merge_query_results_with_labels(
        query_results, labels, paper_eval=paper_eval
    )
    labelled_results.sort_values(by=[QUERY_COL, RANK_COL], ignore_index=True)
    return labelled_results


def _query_elasticsearch_claim_search(
    claim_index: ClaimIndex,
    query_text: str,
    query_embedding: List[Any],
    page_size: int,
    search_filter: SearchFilter,
    sort_params: SortParams,
    knn_params: Optional[dict],
    use_vector_sim: bool,
    use_rescore: bool,
) -> pd.DataFrame:
    response = eval_util.execute_elasticsearch_query(
        claim_index,
        query_text,
        query_embedding,
        page_size,
        search_filter,
        sort_params,
        knn_params,
        use_vector_sim=use_vector_sim,
        use_rescore=use_rescore,
    )
    docs = eval_util.parse_results_from_es_response(response)
    # Dedupe claims from the same paper
    unique_docs, deduped_docs = dedup_by_first_unique(
        items=docs,
        selector=(lambda x: x.paper_id),
    )
    for doc in deduped_docs:
        logger.info(f"Skipping claim {doc.claim_id} with used paper id: {doc.paper_id}")
    results_df = pd.DataFrame([dict(doc) for doc in unique_docs])
    results_df["query"] = query_text
    return results_df


def _query_elasticsearch_paper_search(
    paper_index: PaperIndex,
    papers_db: Papers,
    query_text: str,
    query_embedding: List[Any],
    page_size: int,
    search_filter: SearchFilter,
    sort_params: SortParams,
) -> pd.DataFrame:
    response = eval_util.execute_elasticsearch_paper_query(
        paper_index,
        query_text,
        query_embedding,
        page_size,
        search_filter,
        sort_params,
        use_vector_sim=True,
        use_rescore=True,
    )
    docs = eval_util.parse_paper_results_from_es_response(response)
    # Dedupe claims from the same paper
    unique_docs, deduped_docs = dedup_by_first_unique(
        items=docs,
        selector=(lambda x: x.paper_id),
    )
    for doc in deduped_docs:
        logger.warning(f"[?] Skipping claim {doc.claim_id} with used paper id: {doc.paper_id}")
    for doc in unique_docs:
        if doc.paper_id is None:
            logger.error(f"Skipping search result: {doc.doc_id} has no paper id.")
            continue
        paper = papers_db.read_by_id(doc.paper_id)
        if not paper:
            logger.error(f"Skipping search result: unable to find paper with id {doc.paper_id}.")
            continue
        doc.doi = paper.metadata.doi
    # TODO(cvarano): remove Nones from docs
    results_df = pd.DataFrame([dict(doc) for doc in unique_docs])
    results_df["query"] = query_text
    return results_df


def _query_elasticsearch(
    db_env_flag: str,
    search_env_flag: str,
    paper_eval: bool,
    index_name: str,
    query_tuples: List[Tuple[str, str, List[Any]]],
    page_size: int,
    search_filter: SearchFilter,
    sort_params: SortParams,
    knn_params: Optional[dict],
    use_vector_sim: bool,
    use_rescore: bool,
) -> pd.DataFrame:
    search_env = SearchEnv(search_env_flag)
    search = ElasticClient(search_env)
    es_index = PaperIndex(search, index_name) if paper_eval else ClaimIndex(search, index_name)

    if paper_eval:
        db_env = DbEnv(db_env_flag)
        db = MainDbClient(db_env, host_override="127.0.0.1", port_override=5432)
        papers = Papers(db, use_v2=True)

    dfs = []
    for query_text, _, query_embedding in query_tuples:
        if paper_eval:
            df = _query_elasticsearch_paper_search(
                paper_index=es_index,  # type: ignore [arg-type]
                papers_db=papers,
                query_text=query_text,
                query_embedding=query_embedding,
                page_size=page_size,
                search_filter=search_filter,
                sort_params=sort_params,
            )
        else:
            df = _query_elasticsearch_claim_search(
                claim_index=es_index,  # type: ignore [arg-type]
                query_text=query_text,
                query_embedding=query_embedding,
                page_size=page_size,
                search_filter=search_filter,
                sort_params=sort_params,
                knn_params=knn_params,
                use_vector_sim=use_vector_sim,
                use_rescore=use_rescore,
            )
        dfs.append(df)

    es_index.es.close()  # type: ignore [attr-defined]
    if paper_eval:
        papers.connection.close()

    df = pd.concat(dfs, ignore_index=True)
    return df


def _get_search_results(
    db_env_flag: str,
    search_env_flag: str,
    paper_eval: bool,
    index_name: str,
    embedding_model: SimilaritySearchEmbeddingModel,
    num_queries: int,
    page_size: int,
    search_filter: SearchFilter,
    sort_params: SortParams,
    knn_params: Optional[dict],
    quantize_vectors: bool,
    use_vector_sim: bool,
    use_rescore: bool,
) -> pd.DataFrame:
    """
    Returns search results for a set of test queries as a dataframe.

    The field to be displayed in the labelling tool should be named "answer".
    A ranking column is generated for downstream metrics computation.
    """
    query_tuples = eval_util.get_test_queries(embedding_model, num_queries, quantize_vectors)
    query_results = _query_elasticsearch(
        db_env_flag=db_env_flag,
        search_env_flag=search_env_flag,
        paper_eval=paper_eval,
        index_name=index_name,
        query_tuples=query_tuples,
        page_size=page_size,
        search_filter=search_filter,
        sort_params=sort_params,
        knn_params=knn_params,
        use_vector_sim=use_vector_sim,
        use_rescore=use_rescore,
    )
    query_results.rename(columns={"text": "answer"}, inplace=True)
    query_results[RANK_COL] = (
        query_results.groupby(QUERY_COL, as_index=False)
        .apply(lambda x: x.rank(method="first", numeric_only=True, ascending=False))[SCORE_COL]
        .astype(int)
    )
    query_results.sort_values(by=[QUERY_COL, RANK_COL], ignore_index=True)
    return query_results


def _run_evaluation(
    config: dict,
    sort_params: SortParams,
) -> None:
    storage_client = init_storage_client(StorageEnv.PROD)
    assert storage_client.gcloud_client is not None, "gcloud_client must be provided"
    known_background_claim_ids = eval_util.get_background_claim_ids(storage_client)
    gcs_base_path, run_id = gcs_util.get_search_eval_metrics_base_path(config["eval_suffix"])
    config_util.write_yaml_config_to_gcs(storage_client, config, run_id)

    search_filter = make_search_filter(known_background_claim_ids=known_background_claim_ids)

    query_results = _get_search_results(
        db_env_flag=config["db_env"],
        search_env_flag=config["search_env"],
        paper_eval=config["paper_eval"],
        index_name=config["index_name"],
        embedding_model=EMBEDDING_MODEL,
        num_queries=config["num_queries"],
        page_size=config["page_size"],
        search_filter=search_filter,
        sort_params=sort_params,
        knn_params=config.get("knn_params", None),
        quantize_vectors=config["quantize_vectors"],
        use_vector_sim=config["use_vector_sim"],
        use_rescore=config["use_rescore"],
    )
    query_results_output_path = os.path.join(gcs_base_path, "search_results.csv")
    query_results.to_csv(query_results_output_path, index=False)
    logger.info(f"Search results uploaded to: {query_results_output_path}")

    labelled_results = _label_search_results(
        storage_client.gcloud_client, query_results, paper_eval=config["paper_eval"]
    )
    exported = eval_util.export_unlabelled_annotations(
        labelled_results, run_id, paper_eval=config["paper_eval"]
    )
    labelled_results_output_path = os.path.join(gcs_base_path, "search_results_with_labels.csv")
    labelled_results.to_csv(labelled_results_output_path, index=False)
    logger.info(f"Labelled results uploaded to: {labelled_results_output_path}")
    # By default, do not compute metrics if there are unlabelled annotations
    if exported and not config["force_metrics"]:
        return

    # statistics mapping for relevance features
    feature_metrics_dict = {
        feature_name: ["mean", "median"] for feature_name in RELEVANCE_FEATURES
    }
    if not config["paper_eval"]:
        # transform our old labelling scheme to graded relevance by subtracting the max value (3)
        labelled_results[RELEVANCE_COL] = labelled_results[RELEVANCE_COL].transform(
            lambda x: 3 - x  # type: ignore [arg-type]
        )
    # compute query-level metrics
    metrics = relevance.compute_metrics(
        labelled_results,
        k=config["k"],
        relevance_col=RELEVANCE_COL,
        feature_metrics_dict=feature_metrics_dict,
        paper_eval=config["paper_eval"],
    )
    metrics_output_path = os.path.join(gcs_base_path, "query_metrics.csv")
    metrics.to_csv(metrics_output_path, index=False)
    logger.info(f"Query-level relevance metrics uploaded to: {metrics_output_path}")
    # compute aggregate metrics
    agg_metrics = pd.DataFrame(metrics.mean(numeric_only=True)).transpose()
    agg_metrics_output_path = os.path.join(gcs_base_path, "aggregate_metrics.csv")
    agg_metrics.to_csv(agg_metrics_output_path, index=False)
    logger.info(f"Aggregate relevance metrics uploaded to: {agg_metrics_output_path}")


def main(argv=None):
    args = _parse_args(argv)

    config = config_util.load_yaml_config(args.config, args.tag)
    config = _override_yaml_config_with_cli_args(config, args)
    sort_params = config_util.get_sort_params(config)

    # Enable for debugging
    # config_util.pretty_print_yaml_config(config)

    _run_evaluation(
        config=config,
        sort_params=sort_params,
    )


if __name__ == "__main__":
    main()
