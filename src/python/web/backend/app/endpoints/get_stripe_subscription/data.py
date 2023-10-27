from enum import Enum

from pydantic import BaseModel

LOG_ENDPOINT = "get_stripe_subscription"


class LOG_EVENTS(Enum):
    READ_DB = "get_stripe_subscription_from_db"


class GetStripeSubscriptionResponse(BaseModel):
    """
    A response from the /get_stripe_subscription endpoint.
    """

    clerk_user_id: str
    stripe_customer_id: str
    # Stripe User Subscription
    user_subscription: str
