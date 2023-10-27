"""

Iterates over claims in a search index and creates a sitemap for them.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.search.connect import SearchEnv
from common.storage.connect import StorageEnv
from pipelines.sitemap.sitemap import run_sitemap_pipeline

PIPELINE_NAME = "sitemap"


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
        "--input_file_pattern",
        dest="input_file_pattern",
        required=True,
        help="GCS file path that has inference output to load",
    )
    parser.add_argument(
        "--db_env",
        dest="db_env",
        default="dev",
        help="The database environment to read from ('dev'|'prod')",
    )
    parser.add_argument(
        "--search_env",
        dest="search_env",
        default="dev",
        help="The search environment to write to ('dev'|'prod'|'staging')",
    )
    parser.add_argument(
        "--search_index_id",
        dest="search_index_id",
        required=True,
        help="The search index to create a sitemap for",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_sitemap_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=DbEnv(args.db_env),
        storage_env=StorageEnv.PROD,
        search_env=SearchEnv(args.search_env),
        search_index_id=args.search_index_id,
        input_file_pattern=args.input_file_pattern,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
