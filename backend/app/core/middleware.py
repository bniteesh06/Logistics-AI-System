"""Request-scoped middleware: request IDs, timing, and access logging."""
import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.logging import get_logger, new_request_id

logger = get_logger("app.access")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Tags every request with a short id and logs method/path/status/duration."""

    async def dispatch(self, request: Request, call_next):
        request_id = new_request_id()
        start = time.perf_counter()

        response = await call_next(request)

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-Ms"] = str(duration_ms)

        logger.info(
            "%s %s -> %s (%sms)",
            request.method, request.url.path, response.status_code, duration_ms,
        )
        return response
