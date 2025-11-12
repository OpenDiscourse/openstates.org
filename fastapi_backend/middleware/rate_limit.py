"""Rate limiting middleware."""
import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from fastapi_backend.config.settings import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple in-memory rate limiting middleware."""

    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.requests: Dict[str, list] = defaultdict(list)
        self.max_requests = settings.rate_limit_requests
        self.window = settings.rate_limit_window

    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request."""
        # Use X-Forwarded-For header if present, otherwise use client host
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    def _is_rate_limited(self, client_id: str) -> Tuple[bool, int]:
        """Check if client is rate limited."""
        now = time.time()

        # Clean old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if now - req_time < self.window
        ]

        # Check rate limit
        request_count = len(self.requests[client_id])
        if request_count >= self.max_requests:
            return True, request_count

        # Add current request
        self.requests[client_id].append(now)
        return False, request_count + 1

    async def dispatch(self, request: Request, call_next):
        """Check rate limit before processing request."""
        if not settings.rate_limit_enabled:
            return await call_next(request)

        client_id = self._get_client_id(request)
        is_limited, request_count = self._is_rate_limited(client_id)

        if is_limited:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded. Max {self.max_requests} requests per {self.window} seconds.",
                headers={
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time() + self.window)),
                    "Retry-After": str(self.window),
                }
            )

        response = await call_next(request)

        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(self.max_requests - request_count)
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + self.window))

        return response
