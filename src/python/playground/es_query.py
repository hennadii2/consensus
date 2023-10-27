import argparse
import asyncio

from common.search.async_paper_index import AsyncPaperIndex
from common.search.connect import AsyncElasticClient, SearchEnv
from common.search.search_util import DEFAULT_SEARCH_CONFIG, sort_vector_to_ranking_params
from loguru import logger


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index",
        "-i",
        type=str,
        default="paper-index-elser-231017225646",
        help="Index to debug",
    )
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        required=True,
        help="Query to debug",
    )
    parser.add_argument(
        "--sort_vector",
        "-s",
        type=str,
        default=None,
        help="Sort vector to debug",
    )
    return parser.parse_args(argv)


async def main(argv=None):
    args = parse_args(argv)
    search_env = SearchEnv("dev")
    search = AsyncElasticClient(search_env)
    paper_index = AsyncPaperIndex(search, args.index)

    if args.sort_vector:
        ranking_params = sort_vector_to_ranking_params(args.sort_vector)
    else:
        ranking_params = DEFAULT_SEARCH_CONFIG.ranking_params
    logger.info(f"Ranking params: {ranking_params}")

    results = await paper_index.query_elser(
        query_text=args.query,
        page_size=20,
        page_offset=0,
        search_filter=None,
        ranking_params=ranking_params,
    )
    for result in results:
        print(f"{result.paper_id}: {result.title}")

    await paper_index.es.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
