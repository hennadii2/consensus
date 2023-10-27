"""

Iterates over a sci score XLSX file and adds it to the DB.

"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnv
from pipelines.ingest_sciscore.ingest_sciscore import run_ingest_sciscore_pipeline

PIPELINE_NAME = "ingest-sciscore"


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
        help="GCS file path that has inference output to load",
    )
    parser.add_argument(
        "--db_env",
        dest="db_env",
        default="dev",
        help="The database environment to read from ('dev'|'prod')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_ingest_sciscore_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env=DbEnv(args.db_env),
        input_path=args.input_path,
    )


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
