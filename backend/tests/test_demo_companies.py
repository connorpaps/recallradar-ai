import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.db.models import Base, InventoryItem, Recall, RecallMatch, UploadedFile
from app.services.matching import run_matching
from app.services.seed import list_demo_companies, seed_company_inventory, seed_inventory, seed_portfolio_demo
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


@pytest.mark.asyncio
async def test_portfolio_demo_creates_known_confidence_mix(session) -> None:
    result = await seed_portfolio_demo(session)

    assert result["recalls_created"] == 10
    assert result["inventory_created"] == 24
    assert result["matches_created"] == 8

    repeat = await seed_portfolio_demo(session)
    assert repeat["inventory_created"] == 0

    confidence_counts = dict(
        (
            await session.execute(
                select(RecallMatch.confidence, func.count()).group_by(RecallMatch.confidence)
            )
        ).all()
    )
    assert confidence_counts["high"] >= 3
    assert confidence_counts["medium"] >= 3


@pytest.mark.asyncio
async def test_portfolio_demo_refuses_to_replace_uploaded_inventory(session) -> None:
    upload = UploadedFile(file_type="inventory_csv", original_filename="customer.csv", status="processed")
    session.add(upload)
    await session.flush()
    session.add(InventoryItem(product_name="Customer Product", uploaded_file_id=upload.id, raw_row={"source": "upload"}))
    await session.commit()

    with pytest.raises(ValueError, match="demo workspace"):
        await seed_portfolio_demo(session)

    assert await session.scalar(select(InventoryItem.product_name)) == "Customer Product"
    assert await session.scalar(select(func.count(Recall.id)).where(Recall.source == "demo")) == 0


@pytest.mark.asyncio
async def test_portfolio_demo_does_not_call_optional_ai(monkeypatch, session) -> None:
    from app.services import matching, seed

    async def fail_if_called(*args, **kwargs):
        raise AssertionError("optional AI must not run in portfolio demo mode")

    monkeypatch.setattr(seed.ai_provider, "summarize", fail_if_called)
    monkeypatch.setattr(matching.ai_provider, "semantic_similarity", fail_if_called)

    result = await seed_portfolio_demo(session)

    assert result["matches_created"] == 8


@pytest.mark.asyncio
async def test_demo_company_selector_refuses_to_replace_uploaded_inventory(session) -> None:
    upload = UploadedFile(file_type="inventory_csv", original_filename="customer.csv", status="processed")
    session.add(upload)
    await session.flush()
    session.add(InventoryItem(product_name="Customer Product", uploaded_file_id=upload.id, raw_row={"source": "upload"}))
    await session.commit()

    with pytest.raises(ValueError, match="uploaded inventory"):
        await seed_company_inventory(session, "oak_ember_steakhouse")

    assert await session.scalar(select(InventoryItem.product_name)) == "Customer Product"
