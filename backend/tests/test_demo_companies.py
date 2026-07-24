import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base, InventoryItem, Recall, RecallMatch
from app.services.matching import run_matching
from app.services.seed import list_demo_companies, seed_company_inventory, seed_inventory
from app.services.text import normalize_brand, normalize_text


@pytest.fixture
async def session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as test_session:
        yield test_session
    await engine.dispose()


async def add_live_spinach_recall(session) -> None:
    session.add(
        Recall(
            source="openfda",
            source_recall_id="LIVE-TEST-001",
            product_description="Fresh Valley Organic Baby Spinach 5 oz clamshell",
            brand_name="Fresh Valley",
            recalling_firm="Fresh Valley Foods Inc.",
            classification="Class I",
            reason_for_recall="Potential Listeria contamination",
            distribution_pattern="Nationwide",
            normalized_product_name=normalize_text("Fresh Valley Organic Baby Spinach 5 oz clamshell"),
            normalized_brand_name=normalize_brand("Fresh Valley"),
            raw_payload={},
        )
    )
    await session.commit()


def test_lists_eight_demo_company_profiles() -> None:
    companies = list_demo_companies()
    assert len(companies) == 8
    assert any(company["id"] == "metro_mart_grocery" and company["recommended"] for company in companies)
    assert all(company["item_count"] >= 20 for company in companies)


@pytest.mark.asyncio
async def test_seed_company_replaces_inventory_and_clears_matches(session) -> None:
    await add_live_spinach_recall(session)
    first = await seed_company_inventory(session, "metro_mart_grocery")
    await run_matching(session)
    assert first["created"] >= 20
    assert await session.scalar(select(func.count(RecallMatch.id))) > 0

    second = await seed_company_inventory(session, "oak_ember_steakhouse")
    match_count = await session.scalar(select(func.count(RecallMatch.id)))
    inventory_count = await session.scalar(select(func.count(InventoryItem.id)))
    company_rows = (
        await session.scalars(select(InventoryItem).where(InventoryItem.raw_row["demo_company_id"].as_string() == "oak_ember_steakhouse"))
    ).all()
    assert second["company"]["name"] == "Oak & Ember Steakhouse"
    assert match_count == 0
    assert inventory_count == second["created"]
    assert len(company_rows) == second["created"]
    assert all(item.location_type for item in company_rows)


@pytest.mark.asyncio
async def test_legacy_seed_inventory_uses_default_company(session) -> None:
    created = await seed_inventory(session)
    item = await session.scalar(select(InventoryItem).limit(1))
    assert created >= 20
    assert item.raw_row["demo_company_id"] == "metro_mart_grocery"
