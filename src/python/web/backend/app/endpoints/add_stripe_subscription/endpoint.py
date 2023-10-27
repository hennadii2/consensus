from datetime import datetime, timezone

from common.db.customer_subscriptions import CustomerSubscriptions
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.endpoints.add_stripe_subscription.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    AddStripeSubscriptionRequest,
    AddStripeSubscriptionResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.post("/", response_model=AddStripeSubscriptionResponse)
def add_stripe_subscription(
    request: Request,
    data: AddStripeSubscriptionRequest,
) -> AddStripeSubscriptionResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    subscriptions = CustomerSubscriptions(db.connection)

    try:
        ret = False
        if data.stripe_customer_id and len(data.stripe_customer_id) > 0:
            log_add_stripe_subscription_to_db_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.WRITE_DB.value,
            )
            subscriptions.write_subscription_by_stripe_customer_id(
                stripe_customer_id=data.stripe_customer_id,
                stripe_json_data=data.user_subscription,
                timestamp=datetime.now(timezone.utc),
                commit=True,
            )
            log_add_stripe_subscription_to_db_timing_event()
            ret = True

        response = AddStripeSubscriptionResponse(subscription_added=ret)

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed to run add_stripe_subscription for: {data.stripe_customer_id}")
        raise HTTPException(status_code=500, detail=str(e))
