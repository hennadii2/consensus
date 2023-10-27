import argparse

from common.config.constants import (
    REPO_PATH_WEB_DATA_DISPUTED_JSON,
    REPO_PATH_WEB_DATA_QUERIES_JSON,
)
from common.storage.connect import StorageClient, StorageEnv, init_storage_client
from common.storage.disputed_results import parse_data as parse_disputed_data
from common.storage.disputed_results import write_disputed_results_text
from common.storage.example_queries import parse_data as parse_example_queries_data
from common.storage.example_queries import write_example_queries_text
from loguru import logger


def push_example_queries_to_blob(storage_client: StorageClient):
    with open(REPO_PATH_WEB_DATA_QUERIES_JSON) as f:
        text = f.read()

        try:
            parse_example_queries_data(text)
        except Exception as e:
            logger.error(f"Failed to push example queries: {e}")
            raise e

        url = write_example_queries_text(client=storage_client, text=text)
        logger.info(f"Pushed example queries to: {url}")


def push_disputed_results_to_blob(storage_client: StorageClient):
    with open(REPO_PATH_WEB_DATA_DISPUTED_JSON) as f:
        text = f.read()

        try:
            parse_disputed_data(text)
        except Exception as e:
            logger.error(f"Failed to push disputed results: {e}")
            raise e

        url = write_disputed_results_text(client=storage_client, text=text)
        logger.info(f"Pushed disputed results to: {url}")


def main(argv=None):
    """
    Overwrites current version of queries.json on blob store.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        dest="env",
        default="dev",
        help="The storage environment to write to ('dev'|'prod')",
    )
    args, _ = parser.parse_known_args(argv)

    storage_env = StorageEnv(args.env)
    storage_client = init_storage_client(env=storage_env)
    push_example_queries_to_blob(storage_client)
    push_disputed_results_to_blob(storage_client)


if __name__ == "__main__":
    main()
