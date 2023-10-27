from fastapi import Request
from fastapi.responses import JSONResponse
from loguru import logger
from web.backend.app.common.auth import get_user
from web.backend.app.common.rate_limit import denied_by_rate_limit
from web.backend.app.state import SharedState


class RateLimitMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope)
        shared: SharedState = request.app.state.shared

        request_is_rate_limited = False
        user_id = None
        user_ip = None
        try:
            user = get_user(request=request, env=shared.config.auth_env)
            if not user.verified_by_api_key:
                # For now just skip rate limiting if we the test API key is set.
                user_id = None if user.auth is None else user.auth.user_id
                user_ip = user.ip_address
                request_is_rate_limited = False
                request_is_rate_limited = denied_by_rate_limit(
                    redis=shared.redis,
                    url=str(request.url),
                    user=user_id,
                    ip_address=user_ip,
                )
        except Exception as e:
            # Try rate limiting in a local environment as best effort
            if shared.config.is_local_env:
                logger.info(f"Failed to rate limit: {e}")
            else:
                return await JSONResponse(content=str(e), status_code=500)(scope, receive, send)

        if request_is_rate_limited:
            logger.info(f"Request rate limited: id {user_id}: ip {user_ip}: url {request.url}")
            return await JSONResponse(content="", status_code=429)(scope, receive, send)

        await self.app(scope, receive, send)
