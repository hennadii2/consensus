from common.db.customer_subscriptions import CustomerSubscriptions
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.endpoints.delete_stripe_subscription.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    DeleteStripeSubscriptionResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.delete("/{stripe_customer_id}", response_model=DeleteStripeSubscriptionResponse)
def delete_stripe_subscription(
    request: Request,
    stripe_customer_id: str,
) -> DeleteStripeSubscriptionResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    subscriptions = CustomerSubscriptions(db.connection)

    try:
        ret = False
        if stripe_customer_id and len(stripe_customer_id) > 0:
            log_delete_stripe_subscription_from_db_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.DELETE_DB.value,
            )

            subscriptions.remove_subscription_by_stripe_customer_id(
                stripe_customer_id=stripe_customer_id, commit=True
            )

            log_delete_stripe_subscription_from_db_timing_event()
            ret = True

        logger.info(f"delete_from_subscriptions: {stripe_customer_id} {ret}")
        response = DeleteStripeSubscriptionResponse(
            stripe_customer_id=stripe_customer_id,
            success=ret,
        )

        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(
            f"""Failed to run delete_stripe_subscription for:
            stripe_customer_id={stripe_customer_id}"""
        )
        raise HTTPException(status_code=500, detail=str(e))
