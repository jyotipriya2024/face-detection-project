# apps/inference_server/middleware/rate_limiter.py
"""
Simple in-memory sliding-window rate limiter middleware.
Limits each client IP to MAX_REQUESTS per WINDOW_SECONDS.
"""

from __future__ import annotations
import time
from collections import defaultdict, deque

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

MAX_REQUESTS = 60        # requests per window
WINDOW_SECONDS = 60.0    # sliding window size


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Sliding-window rate limiter keyed by client IP.
    Returns HTTP 429 if the rate limit is exceeded.
    """

    def __init__(self, app, max_requests: int = MAX_REQUESTS,
                 window_seconds: float = WINDOW_SECONDS):
        super().__init__(app)
        self.max_requests = max_requests
        self.window = window_seconds
        self._requests: dict[str, deque] = defaultdict(deque)

    async def dispatch(self, request: Request,
                       call_next) -> Response:
        client_ip = request.client.host if request.client else 'unknown'
        now = time.monotonic()
        window = self._requests[client_ip]

        # Remove timestamps outside the sliding window
        while window and window[0] < now - self.window:
            window.popleft()

        if len(window) >= self.max_requests:
            return Response(
                content='{"detail":"Rate limit exceeded"}',
                status_code=429,
                media_type='application/json',
            )

        window.append(now)
        return await call_next(request)
