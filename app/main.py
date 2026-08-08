from fastapi import FastAPI
from app.middleware.ratelimit import rate_limiter
from app.middleware.timing import TimingMiddleware
from app.middleware.errors import ErrorMiddleware
from app.core.logging_middleware import LoggingMiddleware
from app.routers import health, auth, urls, redirect
from starlette.middleware.base import BaseHTTPMiddleware
import sentry_sdk, os

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    send_default_pii=True,
    traces_sample_rate=1.0,
)

app = FastAPI()
# we seperate stack so that we dont crash everyhting cause of  wrong postioning
# 1. Middleware stack
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(ErrorMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limiter)

# 2. Explicit static routes FIRST
@app.get("/")
def root():
    return {"status": "URL Shortener API is running"}

@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0

# 3. Static/Monitoring routers
app.include_router(health.router)

# 4. Feature routers (Auth, Urls, and finally Redirect with `/{code}`)
app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(redirect.router)