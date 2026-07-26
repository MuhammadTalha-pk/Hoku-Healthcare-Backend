"""In-memory rate limiting.

Original rate-limiting scope: Faisal Majeed.
Adapted during integration to avoid a framework-specific dependency.
"""

import threading
import time
from collections import defaultdict, deque

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.config import settings


class InMemoryRateLimiter:
    def __init__(self, requests: int, window_seconds: int):
        self.requests = requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str) -> tuple[bool, int, int]:
        now = time.monotonic()
        cutoff = now - self.window_seconds
        with self._lock:
            bucket = self._hits[key]
            while bucket and bucket[0] <= cutoff:
                bucket.popleft()
            if len(bucket) >= self.requests:
                retry_after = max(1, int(self.window_seconds - (now - bucket[0])))
                return False, 0, retry_after
            bucket.append(now)
            return True, max(0, self.requests - len(bucket)), 0


limiter = InMemoryRateLimiter(settings.RATE_LIMIT_REQUESTS, settings.RATE_LIMIT_WINDOW_SECONDS)


def add_rate_limit_middleware(app: FastAPI) -> None:
    if not settings.RATE_LIMIT_ENABLED:
        return

    @app.middleware("http")
    async def rate_limit(request: Request, call_next):
        if request.url.path in {"/", "/docs", "/redoc", "/openapi.json", f"{settings.API_V1_PREFIX}/health"}:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        allowed, remaining, retry_after = limiter.allow(client)
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"success": False, "status_code": 429, "message": "Rate limit exceeded", "path": request.url.path},
                headers={"Retry-After": str(retry_after)},
            )
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response
