import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

#  this one will configure standard Python logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("fastapi_app")

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # we use this to process the request and get the response
        response = await call_next(request)
        
        # Calculate process time
        process_time = time.time() - start_time
        formatted_process_time = f"{process_time:.4f}s"
        
        # Log request details
        logger.info(
            f"Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {formatted_process_time}"
        )
        
        # Adds custom header tracking duration
        response.headers["X-Process-Time"] = formatted_process_time
        return response