from fastapi import APIRouter
from web.chat_gpt_plugin.app.endpoints.search.endpoint import router as search

router = APIRouter()

router.include_router(search, tags=["search"])
