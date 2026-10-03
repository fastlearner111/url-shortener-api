import logging
import os

import redis
from fastapi import Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)

RATE_LIMIT = int(os.getenv("RATE_LIMIT", "10"))
WINDOW_SIZE = 60
EXEMPT_PREFIXES = ("/docs", "/redoc", "/openapi.json", "/health")

# Short timeouts so a dead Redis can't make every request hang.
limiter_redis = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    socket_connect_timeout=1,
    socket_timeout=1,
)


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


async def rate_limiter(request: Request, call_next):
    if os.environ.get("TESTING") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return await call_next(request)
    if request.url.path.startswith(EXEMPT_PREFIXES):
        return await call_next(request)

    key = f"rate:{_client_ip(request)}"
    try:
        # Creates the key WITH its expiry, only if it doesn't exist yet.
        limiter_redis.set(key, 0, ex=WINDOW_SIZE, nx=True)
        count = limiter_redis.incr(key)
        if count > RATE_LIMIT:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Slow down."},
            )
    except redis.RedisError:
        logger.warning("rate limiter: Redis unavailable, failing open")

    return await call_next(request)