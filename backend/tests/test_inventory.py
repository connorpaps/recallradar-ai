import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base, InventoryItem, UploadedFile
from app.services.inventory import import_inventory_csv
from app.services.text import parse_optional_date, parse_optional_decimal


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as test_session:
        yield test_session
    await engine.dispose()


def test_date_parser_accepts_iso_date() -> None:
    assert parse_optional_date("2026-07-22").isoformat() == "2026-07-22"


def test_date_parser_rejects_bad_date() -> None:
    assert parse_optional_date("07/22/2026") is None


def test_decimal_parser_rejects_bad_quantity() -> None:
    assert parse_optional_decimal("many") is None


@pytest.mark.asyncio
async def test_inventory_csv_import_rejects_empty_csv(session) -> None:
    with pytest.raises(ValueError, match="at least one data row"):
        await import_inventory_csv(session, "empty.csv", b"product_name,quantity\n")


@pytest.mark.asyncio
async def test_inventory_csv_import_rejects_extra_values(session) -> None:
    with pytest.raises(ValueError, match="more values than its header"):
        await import_inventory_csv(session, "invalid.csv", b"product_name,quantity\nApples,4,unexpected\n")


@pytest.mark.asyncio
async def test_inventory_csv_import_enforces_row_limit(session, monkeypatch) -> None:
    from app.config import get_settings

    settings = get_settings()
    monkeypatch.setattr(settings, "max_csv_rows", 1)
    content = b"product_name\nApples\nOranges\n"

    with pytest.raises(ValueError, match="cannot exceed 1 rows"):
        await import_inventory_csv(session, "too-many.csv", content)


@pytest.mark.asyncio
async def test_inventory_csv_import_accepts_valid_rows_without_raw_response_data(session) -> None:
    result = await import_inventory_csv(session, "inventory.csv", b"product_name,brand,quantity\nApples,Acme,4\n")

    assert result["valid_row_count"] == 1
    item = (await session.scalars(select(InventoryItem))).one()
    assert item.product_name == "Apples"
    upload = await session.get(UploadedFile, result["uploaded_file_id"])
    assert upload is not None
