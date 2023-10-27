"""
Iterates over paper feature records and writes an entry into the paper_records
table, abstract_records table, and write the abstract to GCS.
"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.storage.connect import StorageEnv
from pipelines.records.populate_paper_and_abstract_tables.pipeline import run_pipeline

PIPELINE_NAME = "populate-paper-and-abstract-tables"


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
        "--input_patterns",
        action="append",
        dest="input_patterns",
        required=True,
        help="GCS file patterns that contain record parquets to ingest",
    )
    parser.add_argument(
        "--db_env",
        dest="db_env",
        default="dev",
        help="The database environment to write to ('dev'|'prod-ingest')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    db_env = DbEnv(args.db_env)
    if db_env != DbEnv.PROD_INGEST and db_env != DbEnv.DEV:
        logging.error(f"You can only ingest into prod-ingest or dev, not {db_env}.")
        return
    storage_env = StorageEnv.PROD if db_env == DbEnv.PROD_INGEST else StorageEnv(args.db_env)

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=db_env,
        storage_env=storage_env,
        input_patterns=args.input_patterns,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
