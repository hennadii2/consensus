import argparse
import asyncio
import json

from common.search.async_paper_index import AsyncPaperIndex
from common.search.connect import AsyncElasticClient, SearchEnv
from common.search.search_util import DEFAULT_SEARCH_CONFIG


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        "-q",
        type=str,
        required=True,
        help="Query to debug",
    )
    parser.add_argument(
        "--paper-id",
        "-p",
        type=str,
        required=True,
        help="Paper to debug",
    )
    return parser.parse_args(argv)


async def main(argv=None):
    args = parse_args(argv)
    search_env = SearchEnv("dev")
    search = AsyncElasticClient(search_env)
    paper_index = AsyncPaperIndex(search, "elser-papers-test")

    response = await paper_index.query(
        query_text=args.query,
        page_size=10,
        page_offset=0,
        search_filter=None,
        sort_params=DEFAULT_SEARCH_CONFIG.metadata_sort_params,
        debug_paper_id=args.paper_id,
    )

    print(json.dumps(response[0].debug_explanation, indent=2))

    await paper_index.es.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
