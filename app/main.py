from fastapi import FastAPI
from app.middleware.ratelimit import rate_limiter
from app.middleware.logging import LoggingMiddleware
from app.middleware.timing import TimingMiddleware
from app.routers import auth, urls, redirect
from app.middleware.errors import ErrorMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

app = FastAPI()


app.include_router(auth.router)
app.include_router(urls.router)
app.include_router(redirect.router)
app.add_middleware(LoggingMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(ErrorMiddleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=rate_limiter)

@app.get("/")
def root():
    return {"status": "URL Shortener API is running"}
