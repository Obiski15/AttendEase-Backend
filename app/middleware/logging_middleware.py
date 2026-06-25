import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        client_host = request.client.host if request.client else "unknown"
        from app.core.context import client_ip_var
        client_ip_var.set(client_host)
        
        method = request.method
        url = str(request.url)

        try:
            response = await call_next(request)
        except Exception as e:
            duration_ms = (time.perf_counter() - start_time) * 1000.0
            logger.error(
                f"Request failed: {method} {url} - Error: {str(e)}",
                extra={
                    "method": method,
                    "url": url,
                    "client_host": client_host,
                    "duration_ms": round(duration_ms, 2),
                    "status_code": 500,
                    "error": str(e),
                },
                exc_info=True,
            )
            raise e

        duration_ms = (time.perf_counter() - start_time) * 1000.0
        status_code = response.status_code

        logger.info(
            f"{method} {url} - {status_code} - Completed in {duration_ms:.2f}ms",
            extra={
                "method": method,
                "url": url,
                "client_host": client_host,
                "duration_ms": round(duration_ms, 2),
                "status_code": status_code,
            },
        )
        return response
