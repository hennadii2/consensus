"""

Iterates over generated study type data and adds them to the database.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from pipelines.study_types_ingest.pipeline import run_pipeline

PIPELINE_NAME = "study-types-ingest"


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
        help="The database environment to read from ('dev'|'prod-ingest')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    db_env = DbEnv(args.db_env)
    if db_env == DbEnv.PROD:
        logging.error("You should not ingest into prod directly. Please use prod-ingest.")
        return
    if db_env != DbEnv.PROD_INGEST and db_env != DbEnv.DEV:
        logging.error(f"You can only ingest into prod-ingest or dev, not {db_env}.")
        return

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=db_env,
        input_file_pattern=args.input_file_pattern,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
