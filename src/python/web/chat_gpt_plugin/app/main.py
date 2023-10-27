import os
import sys
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urljoin, urlparse

import google.cloud.logging
import uvicorn
import yaml
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles
from google.cloud.logging.handlers import CloudLoggingHandler, setup_logging
from loguru import logger
from web.chat_gpt_plugin.app.common.config_parse import parse_ai_plugin_config
from web.chat_gpt_plugin.app.config import (
    DEPLOYED_URLS_TO_OPENAI_VERIFICATION_TOKENS,
    PUBLIC_DIR,
    TITLE,
    VERSION,
    generate_config,
    get_log_level,
    get_port,
    is_local_env,
)
from web.chat_gpt_plugin.app.router import router
from web.chat_gpt_plugin.app.state import initialize_shared_state


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
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://chat.openai.com"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.mount(
        "/images",
        StaticFiles(directory=os.path.join(PUBLIC_DIR, "images")),
        name="images",
    )
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


@app.get("/.well-known/ai-plugin.json")
def ai_plugin_json(request: Request):
    with open(os.path.join(PUBLIC_DIR, ".well-known/ai-plugin.json")) as f:
        ai_plugin_json_text = f.read()
        if not ai_plugin_json_text:
            raise HTTPException(status_code=500, detail="Failed to read ai_plugin_json")

        deployed_url = request.app.state.shared.config.deployed_url
        assert deployed_url is not None

        ai_plugin_config = parse_ai_plugin_config(json_text=ai_plugin_json_text)

        api_url_path = urlparse(ai_plugin_config.api.url).path
        ai_plugin_config.api.url = urljoin(deployed_url, api_url_path)

        logo_url_path = urlparse(ai_plugin_config.logo_url).path
        ai_plugin_config.logo_url = urljoin(deployed_url, logo_url_path)

        if ai_plugin_config.auth.type == "service_http":
            if deployed_url in DEPLOYED_URLS_TO_OPENAI_VERIFICATION_TOKENS:
                # Sub in verification token for the given deployment
                if ai_plugin_config.auth.verification_tokens is None:
                    ai_plugin_config.auth.verification_tokens = {}
                token = DEPLOYED_URLS_TO_OPENAI_VERIFICATION_TOKENS[deployed_url]
                ai_plugin_config.auth.verification_tokens["openai"] = token
            else:
                # Otherwise remove auth if a valid token is not configured
                ai_plugin_config.auth.type = "none"
                ai_plugin_config.auth.authorization_type = None
                ai_plugin_config.auth.verification_tokens = None

        ai_plugin_json_text = ai_plugin_config.json(indent=2)
        return Response(content=ai_plugin_json_text, media_type="text/json")


@app.get("/openapi.yaml")
def openapi_yaml():
    openapi_schema = get_openapi(
        title=TITLE,
        version=VERSION,
        summary="Get answers to questions from academic papers.",
        description="A plugin that allows users to ask a question and get answers from academic papers",  # noqa: E501
        routes=router.routes,
    )
    return Response(content=yaml.dump(openapi_schema), media_type="text/yaml")


if __name__ == "__main__":
    uvicorn.run(
        "web.chat_gpt_plugin.app.main:app",
        host="0.0.0.0",
        port=get_port(),
        reload=is_local_env(),
        log_level=get_log_level(),
    )
