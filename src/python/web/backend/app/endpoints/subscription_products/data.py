from enum import Enum

from pydantic import BaseModel

LOG_ENDPOINT = "subscription_product"


class LOG_EVENTS(Enum):
    READ_DB = "read_all_subscription_products_from_db"
    READ_ONE_PRODUCT_DB = "read_one_subscription_product_from_db"


class ProductResponse(BaseModel):
    product_id: str
    product_data: dict


class SubscriptionProductsResponse(BaseModel):
    """
    A response from the /subscription_product endpoint.
    """

    subscription_products: list[ProductResponse]
