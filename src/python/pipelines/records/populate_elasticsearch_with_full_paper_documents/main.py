"""
Iterates over paper feature records and writes full papers to a newly created
Elasticsearch index.
"""
import argparse
import logging

from common.beam.pipeline_config import get_pipeline_config
from common.db.connect import DbEnvInfo
from common.search.connect import SearchEnv
from common.slack import slack_util
from pipelines.records.populate_elasticsearch_with_full_paper_documents.pipeline import (
    run_pipeline,
)

PIPELINE_NAME = "paper-index"


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
        help="The database environment to read from ('dev'|'prod'|'prod-ingest')",
    )
    parser.add_argument(
        "--db_host_override",
        dest="host",
        type=str,
        default=None,
        help="The local db host, when using the cloud SQL proxy.",
    )
    parser.add_argument(
        "--db_port_override",
        dest="port",
        type=int,
        default=None,
        help="The local db port, when using the cloud SQL proxy.",
    )
    parser.add_argument(
        "--search_env",
        dest="search_env",
        default="dev",
        help="The database environment to write to ('dev'|'prod-ingest')",
    )
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to the database",
    )
    args, pipeline_args = parser.parse_known_args(argv)

    db_env_info = DbEnvInfo(args.db_env, args.host, args.port)
    search_env = SearchEnv(args.search_env)
    if search_env != SearchEnv.PROD_INGEST and search_env != SearchEnv.DEV:
        logging.error(f"You can only ingest into search prod-ingest or dev, not {search_env}.")
        return

    if args.no_dry_run and args.runner == "DataflowRunner":
        slack_util.send_dev_notification(f"Starting {PIPELINE_NAME} pipeline")
    pipeline_config = get_pipeline_config(PIPELINE_NAME)
    run_pipeline(
        runner=args.runner,
        project_id=args.gcp_project_id,
        beam_args=pipeline_args,
        config=pipeline_config,
        dry_run=(not args.no_dry_run),
        db_env_info=db_env_info,
        search_env=search_env,
        input_patterns=args.input_patterns,
    )
    if args.no_dry_run and args.runner == "DataflowRunner":
        slack_util.send_dev_notification(f"Finished {PIPELINE_NAME} pipeline")


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.INFO)
    main()
