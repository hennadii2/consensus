from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/healthcheck")
def healthcheck(request: Request):
    if not request.app.state.model:
        return JSONResponse({"status": "services not ready"}, status_code=503)

    return JSONResponse({"status": "alive"}, status_code=200)
