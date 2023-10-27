from enum import Enum

from pydantic import BaseModel

LOG_ENDPOINT = "add_stripe_subscription"


class LOG_EVENTS(Enum):
    WRITE_DB = "add_stripe_subscription_to_db"


class AddStripeSubscriptionRequest(BaseModel):
    stripe_customer_id: str
    # Stripe Customer ID
    user_subscription: str
    # Stripe Subscription JSON string


class AddStripeSubscriptionResponse(BaseModel):
    """
    A response from the /add_stripe_subscription endpoint.
    """

    subscription_added: bool
