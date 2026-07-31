from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from threading import Lock
from time import monotonic

from fastapi import Request


@dataclass(frozen=True)
class RateLimitDecision:
    allowed: bool
    retry_after_seconds: int = 0


class InMemoryRateLimiter:
    """Best-effort single-process sliding-window limiter for the public demo."""

    def __init__(self) -> None:
        self._events: dict[tuple[str, str], deque[float]] = defaultdict(deque)
        self._lock = Lock()
        self._last_cleanup = 0.0

    def check(self, key: str, bucket: str, limit: int, window_seconds: int, now: float | None = None) -> RateLimitDecision:
        if limit <= 0 or window_seconds <= 0:
            return RateLimitDecision(allowed=True)

        current = monotonic() if now is None else now
        cutoff = current - window_seconds
        event_key = (key, bucket)
        with self._lock:
            events = self._events[event_key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                retry_after = max(1, int(events[0] + window_seconds - current + 0.999))
                return RateLimitDecision(allowed=False, retry_after_seconds=retry_after)
            events.append(current)
            self._cleanup_expired(current, window_seconds)
            return RateLimitDecision(allowed=True)

    def _cleanup_expired(self, now: float, window_seconds: int) -> None:
        if now - self._last_cleanup < window_seconds:
            return
        cutoff = now - window_seconds
        expired = [key for key, events in self._events.items() if not events or events[-1] <= cutoff]
        for key in expired:
            self._events.pop(key, None)
        self._last_cleanup = now

    def clear(self) -> None:
        with self._lock:
            self._events.clear()
            self._last_cleanup = 0.0


def client_key(request: Request) -> str:
    """Use the ASGI peer address; do not trust spoofable forwarded headers by default."""
    return request.client.host if request.client else "unknown"


def rate_limit_bucket(method: str, path: str) -> str:
    if method == "GET":
        return "read"
    if path == "/inventory/upload":
        return "upload"
    return "action"
