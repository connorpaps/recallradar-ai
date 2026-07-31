import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base
from app.services import openfda
from app.db.models import ImportStatus
from app.services.openfda import get_openfda_import_status, import_openfda_recalls, serialize_openfda_import_status


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as test_session:
        yield test_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_imports_real_openfda_recalls(session) -> None:
    result = await import_openfda_recalls(session, limit=1, since=None)
    status = serialize_openfda_import_status(await get_openfda_import_status(session))

    assert result["imported"] + result["updated"] >= 1
    assert status["status"] == "succeeded"
    assert status["last_success_at"] is not None


def test_import_status_does_not_expose_internal_error_details() -> None:
    status = ImportStatus(source="openfda", status="failed", error="secret upstream URL and token")

    serialized = serialize_openfda_import_status(status)

    assert serialized["error"] == "The latest openFDA refresh failed."
    assert "secret" not in str(serialized)


@pytest.mark.asyncio
async def test_import_throttle_skips_fresh_success(session, monkeypatch) -> None:
    calls = 0

    async def fake_fetch(limit, since):
        nonlocal calls
        calls += 1
        return [{"recall_number": "THROTTLE-1", "product_description": "Throttle Test Product"}]

    monkeypatch.setattr(openfda, "fetch_openfda_recalls", fake_fetch)

    first = await import_openfda_recalls(session, limit=1, since=None, force=False)
    second = await import_openfda_recalls(session, limit=1, since=None, force=False)

    assert first["refreshed"] is True
    assert second["refreshed"] is False
    assert calls == 1
