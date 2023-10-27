"""

Iterates over claim inference output and updates search index docs with SJR scores from DB.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.search.connect import SearchEnv
from loguru import logger
from pipelines.search_index_update.pipeline import run_search_index_update_pipeline

PIPELINE_NAME = "search-index-update"


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
        "--search_index_id_no_prefix",
        dest="search_index_id",
        help="Elasticsearch index id to send updates to without the prefix (e.g. 'claims-')",
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

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_search_index_update_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=DbEnv(args.db_env),
        search_env=SearchEnv(args.search_env),
        input_file_pattern=args.input_file_pattern,
        search_index_id=args.search_index_id,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
