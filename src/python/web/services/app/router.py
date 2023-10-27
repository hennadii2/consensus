from fastapi import APIRouter
from web.services.app.endpoints.healthcheck import router as healthcheck
from web.services.app.endpoints.yes_no_answer import router as yes_no_answer

router = APIRouter()

router.include_router(yes_no_answer, tags=["yes_no_answer"])
router.include_router(healthcheck, tags=["healthcheck"])
