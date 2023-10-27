import argparse
import time
from collections import defaultdict

import common.search_eval.config_util as config_util
import pandas as pd
from common.models.similarity_search_embedding import SimilaritySearchEmbeddingModel
from common.search.claim_index import ClaimIndex
from common.search.connect import ElasticClient, SearchEnv
from common.search.paper_index import PaperIndex
from common.search.search_util import SortParams, make_search_filter
from common.search_eval import eval_util
from common.storage.connect import StorageEnv, init_storage_client
from loguru import logger
from sentence_transformers import SentenceTransformer

EMBEDDING_MODEL = SimilaritySearchEmbeddingModel(
    model=SentenceTransformer("all-MiniLM-L6-v2"),
    embedding_dimensions=384,
)


def nonnegative_integer(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError(f"{value} is not a nonnegative integer")
    return ivalue


def positive_integer(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(f"{value} is not a positive integer")
    return ivalue


def parse_args(argv):
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
        "--num_queries",
        "-n",
        default=50,
        type=positive_integer,
        help="Number of test queries to evaluate",
    )
    parser.add_argument(
        "--page_size",
        "-s",
        default=20,
        type=positive_integer,
        help="Number of results to return from search request",
    )
    parser.add_argument(
        "--num_repeats",
        "-r",
        type=positive_integer,
        default=1,
        help="Number of times to repeat the query set",
    )
    parser.add_argument(
        "--warmup",
        "-w",
        type=nonnegative_integer,
        default=0,
        help="Number of times to run through the query set before timing",
    )
    return parser.parse_args(argv)


def _run_performance_test(
    search_env_flag: str,
    index_name: str,
    num_queries: int,
    page_size: int,
    num_repeats: int,
    warmup: int,
    sort_params: SortParams,
    paper_eval: bool,
) -> None:
    storage_client = init_storage_client(StorageEnv.PROD)
    assert storage_client.gcloud_client is not None, "gcloud_client must be provided"
    known_background_claim_ids = eval_util.get_background_claim_ids(storage_client)
    search_env = SearchEnv(search_env_flag)
    search = ElasticClient(search_env)
    if paper_eval:
        paper_index = PaperIndex(search, index_name)
    else:
        claim_index = ClaimIndex(search, index_name)

    text_vector_query_tuples = eval_util.get_test_queries(EMBEDDING_MODEL, num_queries)
    query_timings = defaultdict(list)
    for i in range(warmup + num_repeats):
        logger.info(
            f"Iteration {i + 1} of {warmup + num_repeats}: {'warmup' if i < warmup else 'timed'}"
        )
        for orig_text, _, vector in text_vector_query_tuples:
            start = time.time()
            if paper_eval:
                _ = eval_util.execute_elasticsearch_paper_query(
                    paper_index=paper_index,
                    query_text=orig_text,
                    query_vector=vector,
                    size=page_size,
                    search_filter=make_search_filter(),
                    sort_params=sort_params,
                    use_vector_sim=True,
                    use_rescore=True,
                )
            else:
                _ = eval_util.execute_elasticsearch_query(
                    claim_index=claim_index,
                    text_query=orig_text,
                    query_vector=vector,
                    size=page_size,
                    search_filter=make_search_filter(
                        known_background_claim_ids=known_background_claim_ids
                    ),
                    sort_params=sort_params,
                    use_vector_sim=True,
                    use_rescore=True,
                )
            wall_time = time.time() - start
            if i >= warmup:
                query_timings[orig_text].append(wall_time)

    df = pd.DataFrame.from_dict(query_timings, orient="index")
    # TODO(cvarano): write to gcs w/ description
    logger.info(f"\n{df}")
    logger.info(f"\n{df.describe()}")
    # TODO(cvarano): get percentiles instead
    mean_query_df = df.mean(axis=1)
    logger.info(f"\n{mean_query_df}")
    logger.info(f"Total mean query time: {mean_query_df.mean()}")


def main(argv=None):
    args = parse_args(argv)

    config = config_util.load_yaml_config(args.config, args.tag)
    sort_params = config_util.get_sort_params(config)

    _run_performance_test(
        search_env_flag=config["search_env"],
        index_name=config["index_name"],
        num_queries=args.num_queries,
        page_size=args.page_size,
        num_repeats=args.num_repeats,
        warmup=args.warmup,
        sort_params=sort_params,
        paper_eval=config["paper_eval"],
    )


if __name__ == "__main__":
    main()
