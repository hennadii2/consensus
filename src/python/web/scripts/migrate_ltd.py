import os
from argparse import ArgumentParser
from typing import Any

import stripe  # type: ignore
from common.config.constants import REPO_PATH_LOCAL_DOT_ENV
from dotenv import load_dotenv
from loguru import logger

PREMIUM_ZERO_PRICE_ID = "price_1NAeGsF5zSuk8EYS4n9jkRH5"
PREMIUM_PRICES = [
    "price_1NuH2XF5zSuk8EYSIHAqnKuZ",
]
createdCustomers = []
LTD_PRICES = [6500, 19999]


def find_or_create_customer(billingDetail: dict[str, Any], customerEmail: str):
    customer = None
    findCustomersQuery = ""
    if customerEmail == "" or customerEmail is None:
        findCustomersQuery = f'email:"{billingDetail["email"]}"'
    else:
        findCustomersQuery = f'email:"{customerEmail}"'

    customers = stripe.Customer.search(
        query=findCustomersQuery, limit=1, expand=["data.subscriptions"]
    )

    if len(customers.data) == 0:
        if billingDetail["email"] not in createdCustomers:
            logger.info(f"Can not find customer: {billingDetail['email']}")
            logger.info(f"Creating new customer: {billingDetail['email']}")
            customer = stripe.Customer.create(
                email=billingDetail["email"],
                name=billingDetail["name"],
                phone=billingDetail["phone"],
                address=billingDetail["address"],
            )
            createdCustomers.append(billingDetail["email"])
    else:
        customer = customers.data[0]

    return customer


def check_customer_has_premium_subscription(customer: dict) -> bool:
    if (
        "subscriptions" in customer
        and customer["subscriptions"]
        and customer["subscriptions"]["data"]
    ):
        for subscriptionData in customer["subscriptions"]["data"]:
            if subscriptionData.plan.active is True and subscriptionData.plan.id in PREMIUM_PRICES:
                return True
    return False


def create_zero_premium_subscription(customer: dict) -> bool:
    subscription: dict = stripe.Subscription.create(
        customer=customer["id"], items=[{"price": PREMIUM_ZERO_PRICE_ID}]
    )
    if subscription is not None and subscription["status"] == "active":
        return True

    return False


def migrate_ltd_users_to_premium_subscription(amount: int, dry_run: bool) -> int:
    """
    Adds stripe subscription product data into subscription_products tables.
    """
    success_count = 0

    chargeQuery = f'amount={amount} AND status:"succeeded" AND disputed:"false"'
    charges = stripe.Charge.search(query=chargeQuery, limit=100)
    for charge in charges.auto_paging_iter():
        billingDetail = charge.billing_details
        customerEmail = charge.customer

        if dry_run:
            logger.info("[dry_run]: Customer to convert:")
            logger.info(f"[dry_run]: {customerEmail}")
            logger.info(f"[dry_run]: {billingDetail}")
            success_count = success_count + 1
            continue

        customer = find_or_create_customer(billingDetail, customerEmail)
        if customer is not None:
            customerHasPremiumSubscription = check_customer_has_premium_subscription(customer)

            if customerHasPremiumSubscription is False:
                ret = create_zero_premium_subscription(customer)
                if ret is True:
                    logger.info(f"Assigned Customer({customer.email}) to premium subscription")
                    success_count = success_count + 1

    return success_count


def main():
    """
    Migrate customers who purchased LTD products into Premium zero plan.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--no_dry_run",
        action="store_true",
        help="If set, data will be written to stripe",
    )
    args = parser.parse_args()

    load_dotenv(REPO_PATH_LOCAL_DOT_ENV)
    stripe.api_key = os.environ.get("STRIPE_API_KEY", "")

    success_count = 0
    for ltd_price in LTD_PRICES:
        success_count = success_count + migrate_ltd_users_to_premium_subscription(
            amount=ltd_price,
            dry_run=(not args.no_dry_run),
        )
    logger.info(f"Migrated {success_count} customers into premium $0 plan.")


if __name__ == "__main__":
    main()
