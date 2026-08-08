import os
import redis
from fastapi import Request, HTTPException

# Connects to Redis (local dev)
r = redis.Redis(host="localhost", port=6379, db=0)

RATE_LIMIT = 10      # Max requests allwoed
WINDOW_SIZE = 60     # Per 60 seconds

async def rate_limiter(request: Request, call_next):
    # 1 We skip rate limiting entirely when running tests
    if os.environ.get("TESTING") == "1" or os.environ.get("PYTEST_CURRENT_TEST"):
        return await call_next(request)

    # 2. Get client IP safely
    client_ip = request.client.host if request.client else "127.0.0.1"
    key = f"rate:{client_ip}"

    try:
        current = r.get(key)

        if current is None:
            r.set(key, 1, ex=WINDOW_SIZE)
        else:
            current = int(current)
            if current >= RATE_LIMIT:
                raise HTTPException(
                    status_code=429,
                    detail="Too many requests. Slow down."
                )
            r.incr(key)
    except redis.ConnectionError:
        # If Redis is offline during development, don't crash the app
        pass

    return await call_next(request)