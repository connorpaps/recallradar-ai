import pytest
from fastapi import Request
from httpx import ASGITransport, AsyncClient

from app.main import app, rate_limiter, settings
from app.security import InMemoryRateLimiter, client_key, rate_limit_bucket


def test_rate_limiter_allows_limit_then_returns_retry_after() -> None:
    limiter = InMemoryRateLimiter()

    assert limiter.check("127.0.0.1", "action", 2, 60, now=100).allowed
    assert limiter.check("127.0.0.1", "action", 2, 60, now=101).allowed
    blocked = limiter.check("127.0.0.1", "action", 2, 60, now=102)

    assert blocked.allowed is False
    assert blocked.retry_after_seconds == 58


def test_rate_limiter_expires_events_and_clear_resets_state() -> None:
    limiter = InMemoryRateLimiter()

    assert limiter.check("client", "read", 1, 10, now=100).allowed
    assert limiter.check("client", "read", 1, 10, now=109).allowed is False
    assert limiter.check("client", "read", 1, 10, now=110).allowed
    limiter.clear()
    assert limiter.check("client", "read", 1, 10, now=110).allowed


def test_rate_limit_buckets_classify_requests() -> None:
    assert rate_limit_bucket("GET", "/dashboard/summary") == "read"
    assert rate_limit_bucket("POST", "/inventory/upload") == "upload"
    assert rate_limit_bucket("PATCH", "/matches/123/status") == "action"


def test_client_key_uses_peer_address() -> None:
    request = Request({"type": "http", "client": ("192.0.2.10", 1234)})
    assert client_key(request) == "192.0.2.10"


@pytest.mark.asyncio
async def test_http_rate_limit_returns_retry_after_and_health_is_exempt(monkeypatch) -> None:
    monkeypatch.setattr(settings, "rate_limit_read_per_window", 1)
    rate_limiter.clear()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        first = await client.get("/docs")
        second = await client.get("/docs")
        health = await client.get("/health")

    assert first.status_code == 200
    assert second.status_code == 429
    assert second.headers["retry-after"]
    assert second.headers["x-content-type-options"] == "nosniff"
    assert second.headers["x-frame-options"] == "DENY"
    assert health.status_code == 200
    assert health.headers["x-content-type-options"] == "nosniff"
