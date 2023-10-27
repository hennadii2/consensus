import csv
import os
from argparse import ArgumentParser

from common.config.constants import REPO_PATH_LOCAL_DOT_ENV
from common.db.connect import DbEnv, MainDbClient
from common.db.records.paper_records import PaperRecords
from dotenv import load_dotenv
from loguru import logger


def init_database_connection() -> PaperRecords:
    """
    Establishes connection to locally running postgres instance or connection.

    See documentation for established authed local proxy connection:
    https://cloud.google.com/sql/docs/postgres/connect-auth-proxy
    """
    db_password = os.environ["CLOUD_SQL_PROXY_DB_PASSWORD"]
    os.environ[
        "POSTGRES_URI_LOCAL"
    ] = f"postgresql://postgres:{db_password}@127.0.0.1:5432/postgres"

    cxn = MainDbClient(DbEnv.LOCAL)
    assert cxn.info.host == "localhost" or cxn.info.host == "127.0.0.1"
    return PaperRecords(cxn)


def lookup_fields_of_study(
    paper_records: PaperRecords,
    input_csv_filename: str,
    output_csv_filename: str,
):
    total = 0
    skipped = 0
    with open(input_csv_filename, "r") as input_csv:
        reader = csv.DictReader(input_csv)
        if reader.fieldnames is None:
            raise ValueError("input csv must have field names")
        with open(output_csv_filename, "w") as output_csv:
            writer = csv.DictWriter(
                output_csv, fieldnames=list(reader.fieldnames) + ["fields_of_study"]
            )
            writer.writeheader()
            for row in reader:
                total += 1
                paper_id = row["paper_id"]
                paper = paper_records.read_by_id(
                    paper_id=paper_id,
                    active_only=True,
                    max_version=None,
                )
                if not paper:
                    skipped += 1
                    logger.info(f"skipped: {paper_id}")
                    continue
                fields_of_study = [x.string_data for x in paper.metadata.fields_of_study]
                row["fields_of_study"] = str(fields_of_study)
                writer.writerow(row)
                logger.info(f"wrote: {paper_id} {fields_of_study}")
    logger.info("===========================")
    logger.info(f"Total processed: {total}")
    logger.info(f"Skipped: {skipped}")
    logger.info(f"Wrote to file: {total - skipped}")
    logger.info("===========================")


def main():
    """
    Reads an input csv with paper_id column and adds a fields_of_study column.

    If an input row does not have a paper in the paper_records table, it is
    not included in the output_csv.

    To run:
    CLOUD_SQL_PROXY_DB_PASSWORD=<db_password> \
            ./pants run src/python/scripts:lookup_field_of_study_by_paper_id -- \
            --input_csv=<filename> --output_csv=<filename>

    """
    parser = ArgumentParser()
    parser.add_argument(
        "--input_csv",
        dest="input_csv",
        help="Input CSV file with paper_id column.",
        required=True,
    )
    parser.add_argument(
        "--output_csv",
        dest="output_csv",
        help="Output CSV file with added field of study column.",
        required=True,
    )
    args = parser.parse_args()

    load_dotenv(REPO_PATH_LOCAL_DOT_ENV)
    if "CLOUD_SQL_PROXY_DB_PASSWORD" not in os.environ:
        raise ValueError("Missing required env: CLOUD_SQL_PROXY_DB_PASSWORD")

    paper_records = init_database_connection()
    lookup_fields_of_study(
        paper_records=paper_records,
        input_csv_filename=args.input_csv,
        output_csv_filename=args.output_csv,
    )


if __name__ == "__main__":
    main()
