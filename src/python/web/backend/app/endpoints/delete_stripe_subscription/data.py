from enum import Enum

from pydantic import BaseModel

LOG_ENDPOINT = "delete_stripe_subscription"


class LOG_EVENTS(Enum):
    DELETE_DB = "delete_stripe_subscription_from_db"


class DeleteStripeSubscriptionResponse(BaseModel):
    """
    A response from the /delete_stripe_subscription endpoint.
    """

    stripe_customer_id: str
    # Stripe customer Id
    success: bool
    # Success Status
