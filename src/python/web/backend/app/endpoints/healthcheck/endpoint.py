from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from loguru import logger
from web.backend.app.state import SharedState

router = APIRouter()


@router.get("/healthcheck")
async def healthcheck(
    request: Request,
):
    logger.info("Running healthcheck")
    shared: Optional[SharedState] = request.app.state.shared

    if not shared:
        return JSONResponse({"failReason": "search not ready"}, status_code=503)
    if not await shared.async_es.ping():
        return JSONResponse({"failReason": "search ping failed"}, status_code=503)

    db = shared.db()
    if not db:
        return JSONResponse({"failReason": "db not ready"}, status_code=503)

    if not shared or not shared.redis.ping():
        return JSONResponse({"failReason": "redis cache not ready"}, status_code=503)

    return JSONResponse({"status": "alive"}, status_code=200)


@router.get("/_ah/warmup")
async def warmup():
    return JSONResponse({"status": "alive"}, status_code=200)
