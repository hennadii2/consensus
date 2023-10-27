"""

Iterates over claim infernece output and loads it into a search engine index.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.search.connect import SearchEnv
from loguru import logger
from pipelines.search_index.pipeline import run_search_index_pipeline

PIPELINE_NAME = "search-index"


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--gcp_project_id",
        dest="gcp_project_id",
        required=True,
        help="Google cloud project ID",
    )
    parser.add_argument(
        "--runner",
        dest="runner",
        required=True,
        help="Where to run the job. DataflowRunner cloud, DirectRunner local.",
    )
    parser.add_argument(
        "--input_file_pattern",
        dest="input_file_pattern",
        required=True,
        help="GCS file path that has inference output to load",
    )
    parser.add_argument(
        "--input_logs_file_pattern_to_reprocess_failures",
        dest="input_logs_file_pattern_to_reprocess_failures",
        help="GCS file path that has inference output to load",
    )
    parser.add_argument(
        "--add_to_existing_search_index_id",
        dest="add_to_existing_search_index_id",
        help="GCS file path that has inference output to load",
    )
    parser.add_argument(
        "--db_env",
        dest="db_env",
        required=True,
        help="The database environment to read from ('dev'|'prod')",
    )
    parser.add_argument(
        "--search_env",
        dest="search_env",
        required=True,
        help="The search environment to write to ('dev'|'prod-ingest')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    search_env = SearchEnv(args.search_env)
    if search_env == SearchEnv.PROD:
        logger.error("You should not ingest into prod directly. Please use prod-ingest.")
        return
    if search_env != SearchEnv.PROD_INGEST and search_env != SearchEnv.DEV:
        logger.error(f"You can only ingest into prod-ingest or dev, not {search_env}.")
        return

    if (
        args.input_logs_file_pattern_to_reprocess_failures
        and not args.add_to_existing_search_index_id
    ):
        logger.error("Logs file and search index must be set for reprocessing.")
        return

    pipeline_name = (
        PIPELINE_NAME
        if args.add_to_existing_search_index_id is None
        else f"{PIPELINE_NAME}-add-to-existing"
    )
    pipeline_config = get_pipeline_config(pipeline_name)
    run_search_index_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=DbEnv(args.db_env),
        search_env=SearchEnv(args.search_env),
        input_file_pattern=args.input_file_pattern,
        add_to_existing_search_index_id=args.add_to_existing_search_index_id,
        input_logs_file_with_failures=args.input_logs_file_pattern_to_reprocess_failures,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
