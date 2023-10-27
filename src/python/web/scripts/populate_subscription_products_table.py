import json
import os
from argparse import ArgumentParser
from datetime import datetime, timezone

import stripe  # type: ignore
from common.config.constants import REPO_PATH_LOCAL_DOT_ENV
from common.db.connect import DbEnv, MainDbClient
from common.db.subscription_products import PartialSubscriptionProduct, SubscriptionProducts
from dotenv import load_dotenv
from loguru import logger


def init_database_connection(use_cloud_sql_proxy: bool) -> SubscriptionProducts:
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
    assert cxn.info.host == "localhost" or cxn.info.host == "127.0.0.1"
    return SubscriptionProducts(cxn)


def ingest_stripe_subscription_data(
    subscription_products_db: SubscriptionProducts,
) -> int:
    """
    Adds stripe subscription product data into subscription_products tables.
    """
    stripe.api_key = os.environ["STRIPE_API_KEY"]
    products = stripe.Product.search(
        query="active:'true' AND metadata['status']:'active'", limit=10
    )

    success_count = 0
    if products:
        latest_products = []
        for product in products.data:
            prices = stripe.Price.search(
                query=f"product:'{product.id}' AND active:'true'",
                limit=10,
            )
            product["prices"] = prices.data
            print(product)
            latest_products.append(
                PartialSubscriptionProduct(
                    product_id=product.id,
                    json_data=json.dumps(product),
                )
            )
            success_count = success_count + 1

        subscription_products_db.write_latest_subscription_products(
            products=latest_products,
            timestamp=datetime.now(timezone.utc),
            commit=True,
        )

    subscription_products_db.connection.commit()
    return success_count


def main():
    """
    Ingest stripe subscription product data into the local DB.
    """
    parser = ArgumentParser()
    parser.add_argument(
        "--use_cloud_sql_proxy",
        action="store_true",
        help="If set, DB connection to running cloud sql proxy will be used.",
    )
    args = parser.parse_args()

    load_dotenv(REPO_PATH_LOCAL_DOT_ENV)
    if "STRIPE_API_KEY" not in os.environ:
        raise ValueError("Missing required env: STRIPE_API_KEY")
    if args.use_cloud_sql_proxy and "CLOUD_SQL_PROXY_DB_PASSWORD" not in os.environ:
        raise ValueError("Missing required env: CLOUD_SQL_PROXY_DB_PASSWORD")

    subscription_products_db = init_database_connection(args.use_cloud_sql_proxy)
    success_count = ingest_stripe_subscription_data(
        subscription_products_db=subscription_products_db
    )
    logger.info(f"Added {success_count} subscription products to the database")


if __name__ == "__main__":
    main()
