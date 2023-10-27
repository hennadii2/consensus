"""

Iterates over CSV of generated queries and adds them to the autcomplete index.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.search.connect import SearchEnv
from loguru import logger
from pipelines.autocomplete_index.pipeline import run_pipeline

PIPELINE_NAME = "autocomplete-index"


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
        default="DirectRunner",
        help="Where to run the job. DataflowRunner cloud, DirectRunner local.",
    )
    parser.add_argument(
        "--input_path",
        dest="input_path",
        required=True,
        help="GCS file path that has autocomplete queries to load",
    )
    parser.add_argument(
        "--search_env",
        dest="search_env",
        default="dev",
        help="The search environment to write to ('dev'|'prod'|'staging')",
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

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        search_env=search_env,
        input_path=args.input_path,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
