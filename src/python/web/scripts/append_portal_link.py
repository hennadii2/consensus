import csv
import os
from argparse import ArgumentParser

import stripe  # type: ignore
from common.config.constants import REPO_PATH_LOCAL_DOT_ENV
from dotenv import load_dotenv


def find_id_from_email(email: str):
    customers = stripe.Customer.search(query=f'email:"{email}"', limit=1)
    if len(customers.data) > 0:
        return customers.data[0]["id"]

    return None


def generate_portal_link_from_id(customer_id: str):
    portal_url = stripe.billing_portal.Session.create(
        customer=customer_id,
    )
    return portal_url


def process_csv(csv_filename: str):
    rows = []
    outputRows = []
    with open(csv_filename, "r+") as csvfile:
        reader = csv.reader(csvfile, delimiter=" ", quotechar="|")
        for row in reader:
            rows.append(row)

    for row in rows:
        if len(row) > 0:
            email = row[0]
            customer_id = find_id_from_email(email=email)
            if customer_id is not None:
                portal_link = generate_portal_link_from_id(customer_id=customer_id)
                outputRow = {"A": email, "B": portal_link.url}
                outputRows.append(outputRow)
                print(outputRow)

    if len(outputRows) > 0:
        with open(csv_filename, "w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["A", "B"])
            for outputRow in outputRows:
                writer.writerow(outputRow)


def main(argv=None):
    """
    Get email from csv file and append customer portal link to allow users to edit their email
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, metadata will be written to clerk/stripe",
    )
    parser.add_argument(
        "--csv_filename",
        dest="csv_filename",
        help="If set, add missing emails to csv file.",
    )
    args, _ = parser.parse_known_args(argv)
    load_dotenv(REPO_PATH_LOCAL_DOT_ENV)

    if "STRIPE_API_KEY" not in os.environ:
        raise ValueError("Missing required env: STRIPE_API_KEY")

    stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
    process_csv(csv_filename=args.csv_filename)


if __name__ == "__main__":
    main()
