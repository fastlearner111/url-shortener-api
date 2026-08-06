from starlette.middleware.base import BaseHTTPMiddleware

class ErrorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        try:
            return await call_next(request)
        except Exception as e:
            print(f"ERROR: {e}")
            raise e
