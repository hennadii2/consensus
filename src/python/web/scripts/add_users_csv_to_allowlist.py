import argparse
import csv
import json

import requests
from loguru import logger

CLERK_ALLOWLIST_URL = "https://api.clerk.dev/v1/allowlist_identifiers"


def create_clerk_headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def list_users(token: str) -> None:
    """
    Lists all users in a Clerk instance allowlist.
    """
    headers = create_clerk_headers(token)
    response = requests.get(CLERK_ALLOWLIST_URL, headers=headers)
    logger.info(response.status_code)
    logger.info(response.reason)
    logger.info(response.json())


def add_users(token: str, csv_filename: str) -> None:
    """
    Adds all user emails from a CSV file to a Clerk instance allowlist.
    """
    headers = create_clerk_headers(token)

    success = []
    failed = {}
    with open(csv_filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            for email in row:
                payload = {"identifier": email.strip(), "notify": False}
                response = requests.post(
                    CLERK_ALLOWLIST_URL,
                    data=json.dumps(payload),
                    headers=headers,
                )
                if response.status_code != 200:
                    failed[email] = response.json()
                    continue

                success.append(email)

    logger.info(f"Added {len(success)} users and failed to add {len(failed)}")

    if len(failed):
        logger.info("Failed users:")
        for user in failed:
            reason = failed[user]
            logger.info(f"  {user}: {reason}")


def main(argv=None):
    """
    Calls the Clerk API to add or list users.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--clerk_bearer_token",
        dest="clerk_bearer_token",
        required=True,
        help="Clerk backend API token.",
    )
    parser.add_argument(
        "--list_users",
        action="store_true",
        help="If set, prints existing allowlist users",
    )
    parser.add_argument(
        "--add_users_csv_filename",
        dest="add_users_csv_filename",
        help="If set, adds all emails in this CSV to the allowlist",
    )
    args, _ = parser.parse_known_args(argv)

    handled = False

    if args.list_users:
        list_users(args.clerk_bearer_token)
        handled = True

    if args.add_users_csv_filename:
        add_users(args.clerk_bearer_token, args.add_users_csv_filename)
        handled = True

    if not handled:
        logger.error("You must set at least one action argument, see parser options.")
        return


if __name__ == "__main__":
    main()
