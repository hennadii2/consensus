from common.db.customer_subscriptions import CustomerSubscriptions
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.common.auth import get_verified_clerk_user
from web.backend.app.endpoints.get_stripe_subscription.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    GetStripeSubscriptionResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.get("/", response_model=GetStripeSubscriptionResponse)
def get_stripe_subscription(
    request: Request,
    stripe_customer_id: str,
) -> GetStripeSubscriptionResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    customer_subscriptions = CustomerSubscriptions(db.connection)
    clerk_user = get_verified_clerk_user(request=request, env=shared.config.auth_env)

    try:
        log_read_stripe_subscription_from_db_timing_event = time_endpoint_event(
            endpoint=LOG_ENDPOINT,
            event=LOG_EVENTS.READ_DB.value,
        )

        subscription = customer_subscriptions.read_by_stripe_customer_id(stripe_customer_id)

        if clerk_user is None:
            raise ValueError("Unauthed subscription missing clerk token")

        response = GetStripeSubscriptionResponse(
            clerk_user_id=clerk_user.user_id,
            stripe_customer_id=stripe_customer_id,
            user_subscription=("" if subscription is None else subscription.stripe_json_data),
        )
        log_read_stripe_subscription_from_db_timing_event()

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(
            f"Failed to run get_stripe_subscription for: stripe_customer_id={stripe_customer_id}"
        )
        raise HTTPException(status_code=500, detail=str(e))
