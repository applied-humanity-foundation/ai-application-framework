"""Async rate limiter using the token-bucket algorithm.

Enforces per-minute request limits to prevent API throttling.
"""

from __future__ import annotations

import asyncio
import time


class AsyncRateLimiter:
    """Token-bucket rate limiter for async code.

    Args:
        max_requests: Maximum number of requests allowed in ``time_window``.
        time_window: Window size in seconds (default 60 for RPM).
    """

    def __init__(self, max_requests: int = 60, time_window: float = 60.0) -> None:
        self.max_requests = max_requests
        self.time_window = time_window
        self._tokens: float = float(max_requests)
        self._last_refill: float = time.monotonic()
        self._lock = asyncio.Lock()

    def _refill(self) -> None:
        """Add tokens proportional to elapsed time since last refill."""
        now = time.monotonic()
        elapsed = now - self._last_refill
        new_tokens = elapsed * (self.max_requests / self.time_window)
        self._tokens = min(self.max_requests, self._tokens + new_tokens)
        self._last_refill = now

    async def acquire(self) -> None:
        """Wait until a request token is available, then consume one.

        If no token is available the coroutine sleeps until the bucket
        refills enough for one request.
        """
        while True:
            async with self._lock:
                self._refill()
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return
                # Calculate how long until one token is available
                deficit = 1.0 - self._tokens
                wait_seconds = deficit * (self.time_window / self.max_requests)
            await asyncio.sleep(wait_seconds)

    @property
    def available_tokens(self) -> int:
        """Return the current number of available tokens (approximate)."""
        self._refill()
        return int(self._tokens)
