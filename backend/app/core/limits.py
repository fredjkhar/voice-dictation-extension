from collections import defaultdict, deque
from contextlib import asynccontextmanager
import threading
import time
from typing import AsyncIterator


class LimitExceeded(Exception):
    """Raised when an in-process launch guard rejects a request."""


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def allow(self, key: str, *, limit: int, window_seconds: int) -> bool:
        if limit <= 0:
            return True

        now = time.monotonic()
        cutoff = now - window_seconds

        with self._lock:
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()

            if len(hits) >= limit:
                return False

            hits.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


class InProcessConcurrencyLimiter:
    def __init__(self) -> None:
        self._in_flight = 0
        self._lock = threading.Lock()

    @asynccontextmanager
    async def acquire(self, *, limit: int) -> AsyncIterator[None]:
        if limit <= 0:
            yield
            return

        with self._lock:
            if self._in_flight >= limit:
                raise LimitExceeded("concurrency limit exceeded")
            self._in_flight += 1

        try:
            yield
        finally:
            with self._lock:
                self._in_flight = max(0, self._in_flight - 1)

    def reset(self) -> None:
        with self._lock:
            self._in_flight = 0
