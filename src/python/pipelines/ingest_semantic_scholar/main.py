"""
Iterates over all raw paper data in a downloaded semantic scholar dataset,
extracts the metadata, and writes an entry into the papers table and saves
the abstract to blob store.
"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from common.storage.connect import StorageEnv
from pipelines.ingest_semantic_scholar.pipeline import run_pipeline

PIPELINE_NAME = "ingest-semantic-scholar"


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
        "--input_dir",
        dest="input_dir",
        required=True,
        help="GCS bucket that contains raw paper files to ingest",
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
    parser.add_argument(
        "--update_metadata",
        action="store_true",
        default=True,
        help="If set, metadata will be updated",
    )
    parser.add_argument(
        "--update_abstract",
        action="store_true",
        default=True,
        help="If set, abstract will be updated",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    db_env = DbEnv(args.db_env)
    if db_env == DbEnv.PROD:
        logging.error("You should not ingest into prod directly. Please use prod-ingest.")
        return
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
        input_dir=args.input_dir,
        update_metadata=args.update_metadata,
        update_abstract=args.update_abstract,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
