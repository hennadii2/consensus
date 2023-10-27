import csv
import json
import os
from argparse import ArgumentParser
from datetime import datetime, timezone
from typing import Any, Optional

import requests
import stripe  # type: ignore
from common.config.constants import REPO_PATH_LOCAL_DOT_ENV
from common.db.connect import DbEnv, MainDbClient
from common.db.customer_subscriptions import CustomerSubscriptions
from dotenv import load_dotenv
from loguru import logger

CLERK_API_ENDPOINT = "https://api.clerk.com/v1"


def init_database_connection(use_cloud_sql_proxy: bool) -> CustomerSubscriptions:
    """
    Establishes connection to locally running postgres instance or connection.

    To run with Cloud SQL Proxy:
    CLOUD_SQL_PROXY_DB_PASSWORD=<secret> \
            ./pants run src/python/web/scripts:populate_subscription_products_table -- \
            --use_cloud_sql_proxy

    See documentation for established authed local proxy connection:
    https://cloud.google.com/sql/docs/postgres/connect-auth-proxy
    """
    if use_cloud_sql_proxy:
        db_password = os.environ["CLOUD_SQL_PROXY_DB_PASSWORD"]
        os.environ[
            "POSTGRES_URI_LOCAL"
        ] = f"postgresql://postgres:{db_password}@127.0.0.1:5432/postgres"

    cxn = MainDbClient(DbEnv.LOCAL)
    assert cxn.info.host == "localhost"
    return CustomerSubscriptions(cxn)


def create_clerk_headers(token: str) -> dict:
    """
    generate header data for Clerk API calls
    """
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def get_active_subscription(stripe_customer: dict) -> Optional[Any]:
    """
    check if stripe customer has active subscription
    """
    subscriptions = stripe_customer["subscriptions"]["data"]
    if subscriptions:
        for subscription in subscriptions:
            if subscription["status"] == "active":
                return subscription
    return None


def find_clerk_user_by_email(email: str, clerk_token: str):
    """
    Find clerk user with email
    """
    email = email.lower()
    endpoint = (
        f"{CLERK_API_ENDPOINT}/users?limit=2&offset=0&order_by=-created_at&email_address={email}"
    )
    headers = create_clerk_headers(clerk_token)
    response = requests.get(endpoint, headers=headers)

    if response.status_code == 200 and len(response.json()) == 1:
        return response.json()[0]

    return None


def update_clerk_user_with_stripe_customer_id(
    clerk_user_id: str, stripe_customer_id: str, clerk_token: str
):
    """
    Update clerk user's public meta data with stripe customer id
    """

    endpoint = f"{CLERK_API_ENDPOINT}/users/{clerk_user_id}/metadata"
    headers = create_clerk_headers(clerk_token)
    response = requests.patch(
        endpoint,
        data=json.dumps(
            {
                "public_metadata": {
                    "stripeCustomerId": stripe_customer_id,
                },
            }
        ),
        headers=headers,
    )
    if response.status_code == 200:
        logger.info("SUCCESS: updated clerk user's public metadata with stripe customer id")
        return True
    else:
        logger.error("FAILED: update clerk user's public metadata with stripe customer id")
        return False


def update_stripe_meta_data(stripe_customer_id: str, clerk_user_id: str):
    """
    Update stripe customer's meta data with clerk user id
    """

    try:
        stripe.Customer.modify(
            stripe_customer_id,
            metadata={
                "clerkUserId": clerk_user_id,
            },
        )
        logger.info("SUCCESS: update stripe meta data with clerk user id")
    except Exception as e:
        logger.error(f"ERROR: update_stripe_meta_data  {e}")


def add_user_subscription_to_db(
    db: CustomerSubscriptions,
    stripe_customer_id: str,
    subscription: str,
):
    """
    Update user's subscription json data in users db table.
    """
    db.write_subscription_by_stripe_customer_id(
        stripe_customer_id=stripe_customer_id,
        stripe_json_data=subscription,
        timestamp=datetime.now(timezone.utc),
        commit=True,
    )
    logger.info(f"SUCCESS: updated subscription in DB: {stripe_customer_id}")


def append_email_to_csv(email: str, csv_filename: str):
    """
    Append email to csv file.
    """

    row = {"A": email}
    with open(csv_filename, "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row.keys())
        writer.writerow(row)
    return


def map_stripe_customers_to_clerk(
    clerk_token: str,
    csv_file_name: str,
    db: Optional[CustomerSubscriptions],
    dry_run: bool,
):
    stripe_customers = stripe.Customer.search(
        query="metadata['clerkUserId']:null",
        limit=100,
        expand=["data.subscriptions"],
    )

    active_customer_count = 0
    inactive_customer_count = 0
    unmatched_email_count = 0
    matched_email_count = 0
    for stripe_customer in stripe_customers.auto_paging_iter():
        stripe_customer_email = stripe_customer["email"]
        active_subscription = get_active_subscription(stripe_customer)
        if active_subscription is None:
            inactive_customer_count += 1
            continue
        active_customer_count += 1

        clerk_user = find_clerk_user_by_email(
            email=stripe_customer_email,
            clerk_token=clerk_token,
        )
        if clerk_user is not None:
            matched_email_count += 1
            if not dry_run:
                assert db is not None
                logger.info(f"Processing customer: {stripe_customer['email']}")
                clerk_user_id = clerk_user["id"]
                stripe_customer_id = stripe_customer["id"]

                success = update_clerk_user_with_stripe_customer_id(
                    clerk_user_id=clerk_user_id,
                    stripe_customer_id=stripe_customer_id,
                    clerk_token=clerk_token,
                )
                if success:
                    update_stripe_meta_data(
                        stripe_customer_id=stripe_customer_id,
                        clerk_user_id=clerk_user_id,
                    )
                    add_user_subscription_to_db(
                        db=db,
                        stripe_customer_id=stripe_customer_id,
                        subscription=json.dumps(active_subscription),
                    )
        else:
            unmatched_email_count += 1
            if csv_file_name:
                append_email_to_csv(stripe_customer_email, csv_file_name)

    logger.info("--------------------------------------------------------")
    logger.info(f"Total skipped inactive stripe customers: {inactive_customer_count}")
    logger.info(f"Total stripe customers: {active_customer_count}")
    logger.info(f"Total stripe customers with matched Clerk email: {matched_email_count}")
    logger.info(f"Total stripe customers with unmatched Clerk email: {unmatched_email_count}")
    logger.info("--------------------------------------------------------")


def main(argv=None):
    """
    Check stripe customers who purchased premium subscriptions
    Add stripe customer id to clerk user's public meta data.
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
    parser.add_argument(
        "--use_cloud_sql_proxy",
        action="store_true",
        help="If set, DB connection to running cloud sql proxy will be used.",
    )
    args, _ = parser.parse_known_args(argv)
    load_dotenv(REPO_PATH_LOCAL_DOT_ENV)

    if "STRIPE_API_KEY" not in os.environ:
        raise ValueError("Missing required env: STRIPE_API_KEY")
    if "CLERK_SECRET_KEY" not in os.environ:
        raise ValueError("Missing required env: CLERK_SECRET_KEY")
    if args.use_cloud_sql_proxy and "CLOUD_SQL_PROXY_DB_PASSWORD" not in os.environ:
        raise ValueError("Missing required env: CLOUD_SQL_PROXY_DB_PASSWORD")

    if args.no_dry_run and not args.use_cloud_sql_proxy:
        raise ValueError(
            "You must use CLOUD SQL PROXY for non dry run.\n"
            + "Otherwise customers will be written to local DB instead of prod DB."
        )

    stripe.api_key = os.environ.get("STRIPE_API_KEY", "")
    clerk_token = os.environ.get("CLERK_SECRET_KEY", "")

    customer_subscriptions_db = (
        init_database_connection(
            use_cloud_sql_proxy=args.use_cloud_sql_proxy,
        )
        if args.no_dry_run
        else None
    )
    map_stripe_customers_to_clerk(
        clerk_token=clerk_token,
        csv_file_name=args.csv_filename,
        db=customer_subscriptions_db,
        dry_run=(not args.no_dry_run),
    )


if __name__ == "__main__":
    main()
