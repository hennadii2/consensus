import os
import sys
from contextlib import asynccontextmanager
from typing import Any

import google.cloud.logging
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging
from loguru import logger
from web.services.app.config import (
    TITLE,
    VERSION,
    generate_config,
    get_log_level,
    get_port,
    is_local_env,
)
from web.services.app.router import router
from web.services.app.state import initialize_shared_state


def configure_logging() -> None:
    """
    Configure logging library for local or cloud deployment."""

    # Log to stdout by default
    handler: Any = sys.stdout
    try:
        # Try setup google cloud logging, if authenticated
        if not os.environ["KUBERNETES_SERVICE_HOST"]:
            client = google.cloud.logging.Client()
            handler = CloudLoggingHandler(client)
            setup_logging(handler)
            logger.info("Using google cloud logging")
        else:
            logger.info("Using sys.stdout logging")
    except Exception:
        logger.info("Using sys.stdout logging")

    logging_config: dict[Any, Any] = {
        "handlers": [{"sink": handler}],
    }
    logger.remove()
    logger.configure(**logging_config)


@asynccontextmanager
async def lifespan(app: FastAPI):
    configure_logging()
    app.state.shared = initialize_shared_state(config=generate_config())

    yield


def init() -> FastAPI:
    app = FastAPI(title=TITLE, version=VERSION, lifespan=lifespan)
    app.include_router(router)
    return app


app = init()


@app.get("/custom_readiness_check")
@app.post("/custom_readiness_check")
async def custom_readiness_check(request: Request):
    if not request.app.state.shared:
        return JSONResponse({"failReason": "shared_state_not_ready"}, status_code=503)
    return {"status": "ready"}


@app.get("/custom_liveness_check")
@app.post("/custom_liveness_check")
async def custom_liveness_check():
    return {"status": "ready"}


if __name__ == "__main__":
    uvicorn.run(
        "web.services.app.main:app",
        host="0.0.0.0",
        port=get_port(),
        reload=is_local_env(),
        log_level=get_log_level(),
    )
