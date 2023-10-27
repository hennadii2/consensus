import json
from typing import Optional

from common.db.connect import DbEnv
from common.db.db_connection_handler import is_unrecoverable_db_error
from common.db.subscription_products import SubscriptionProducts
from common.logging.timing import time_endpoint_event
from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from web.backend.app.endpoints.subscription_products.data import (
    LOG_ENDPOINT,
    LOG_EVENTS,
    ProductResponse,
    SubscriptionProductsResponse,
)
from web.backend.app.state import SharedState

router = APIRouter()


# Note: keep endpoint non-async until await is used to avoid blocking the main thread
# See https://github.com/Consensus-NLP/common/pull/1120
@router.get("/", response_model=SubscriptionProductsResponse)
def subscription_products(
    request: Request,
    product_id: Optional[str] = None,
) -> SubscriptionProductsResponse:
    shared: SharedState = request.app.state.shared
    db = shared.db()
    subscriptionProducts = SubscriptionProducts(db.connection)
    product_response: list[ProductResponse] = []

    try:
        if product_id is not None:
            log_read_one_product_db_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.READ_ONE_PRODUCT_DB.value,
            )
            subscription_product = subscriptionProducts.read_by_product_id(product_id)

            if subscription_product is not None:
                log_read_one_product_db_timing_event()
                product_response.append(
                    ProductResponse(
                        product_id=subscription_product.stripe_product_id,
                        product_data=json.loads(subscription_product.stripe_json_data),
                    )
                )
        else:
            log_read_all_product_db_timing_event = time_endpoint_event(
                endpoint=LOG_ENDPOINT,
                event=LOG_EVENTS.READ_DB.value,
            )

            log_read_all_product_db_timing_event()
            for subscription_product in subscriptionProducts.read_all(
                version="10/05/2023 18:22:35" if shared.config.db_env == DbEnv.PROD else None
            ):
                product_response.append(
                    ProductResponse(
                        product_id=subscription_product.stripe_product_id,
                        product_data=json.loads(subscription_product.stripe_json_data),
                    )
                )

        response = SubscriptionProductsResponse(subscription_products=product_response)
        return response
    except Exception as e:
        if is_unrecoverable_db_error(e):
            db.close_connection()

        logger.exception(f"Failed to run subscription_product classifier for: {product_id}")
        raise HTTPException(status_code=500, detail=str(e))
