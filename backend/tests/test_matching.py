from decimal import Decimal

import pytest

from app.ai.provider import AiResult
from app.db.models import Base, InventoryItem, Recall, RecallMatch
from app.services import matching
from app.services.matching import confidence_for_score, run_matching, score_recall_inventory, score_recall_inventory_with_ai
from app.services.risk_policy import calculate_exposure, exposure_level_for_score
from app.services.text import normalize_brand, normalize_text
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


def make_recall() -> Recall:
    return Recall(
        source="openfda",
        source_recall_id="T-1",
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


def test_high_confidence_product_and_brand_match() -> None:
    recall = make_recall()
    item = InventoryItem(
        product_name="Fresh Valley Organic Spinach",
        brand="Fresh Valley",
        quantity=Decimal("12"),
        normalized_product_name=normalize_text("Fresh Valley Organic Spinach"),
        normalized_brand=normalize_brand("Fresh Valley"),
        raw_row={},
    )
    result = score_recall_inventory(recall, item)
    assert result["confidence"] == "high"
    assert result["score"] >= 0.75
    assert "Human review is required" in result["explanation"]


def test_unrelated_product_scores_below_persist_threshold() -> None:
    recall = make_recall()
    item = InventoryItem(
        product_name="Oak Table Pasta",
        brand="Oak Table",
        normalized_product_name=normalize_text("Oak Table Pasta"),
        normalized_brand=normalize_brand("Oak Table"),
        raw_row={},
    )
    result = score_recall_inventory(recall, item)
    assert result["score"] < 0.35


def test_confidence_thresholds() -> None:
    assert confidence_for_score(0.8) == "high"
    assert confidence_for_score(0.6) == "medium"
    assert confidence_for_score(0.4) == "low"


def test_exposure_prioritizes_class_i_public_locations() -> None:
    recall = make_recall()
    item = InventoryItem(
        product_name="Fresh Valley Organic Spinach",
        brand="Fresh Valley",
        quantity=Decimal("80"),
        location_type="hospital",
        location_criticality="critical",
        public_serving=True,
        supplier="Fresh Valley Foods",
        raw_row={},
    )
    exposure = calculate_exposure(recall, item, 0.9, [{"name": "upc_match", "score": 1}])
    assert exposure["exposure_level"] in {"critical", "high"}
    assert exposure["exposure_score"] >= 85
    assert "Class I" in exposure["exposure_factors"]["summary"]


def test_exposure_reduces_for_storage_and_resolved_status() -> None:
    recall = make_recall()
    item = InventoryItem(
        product_name="Fresh Valley Organic Spinach",
        brand="Fresh Valley",
        quantity=Decimal("8"),
        location_type="storage",
        location_criticality="storage",
        public_serving=False,
        raw_row={},
    )
    open_exposure = calculate_exposure(recall, item, 0.9, [], status="needs_review")
    resolved_exposure = calculate_exposure(recall, item, 0.9, [], status="resolved")
    assert resolved_exposure["exposure_score"] < open_exposure["exposure_score"]


def test_exposure_level_thresholds() -> None:
    assert exposure_level_for_score(90) == "critical"
    assert exposure_level_for_score(75) == "high"
    assert exposure_level_for_score(55) == "medium"
    assert exposure_level_for_score(20) == "low"


class FakeSession:
    def __init__(self) -> None:
        self.added = []

    def add(self, item) -> None:
        self.added.append(item)


class FakeAiProvider:
    async def semantic_similarity(self, left: str, right: str) -> AiResult:
        return AiResult(0.92, "test-embedding-model", "test-provider", "succeeded", metrics={"score": 0.92})


@pytest.mark.asyncio
async def test_semantic_signal_is_supporting_evidence(monkeypatch) -> None:
    recall = make_recall()
    item = InventoryItem(
        product_name="Fresh Valley Organic Spinach",
        brand="Fresh Valley",
        quantity=Decimal("12"),
        normalized_product_name=normalize_text("Fresh Valley Organic Spinach"),
        normalized_brand=normalize_brand("Fresh Valley"),
        raw_row={},
    )
    session = FakeSession()
    monkeypatch.setattr(matching, "ai_provider", FakeAiProvider())
    result = await score_recall_inventory_with_ai(session, recall, item)
    assert any(signal["name"] == "semantic_similarity" for signal in result["signals"])
    assert result["score"] <= 1
    assert session.added


@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    maker = async_sessionmaker(engine, expire_on_commit=False)
    async with maker() as test_session:
        yield test_session
    await engine.dispose()


@pytest.mark.asyncio
async def test_run_matching_defaults_to_live_recalls(db_session) -> None:
    live_recall = make_recall()
    demo_recall = make_recall()
    demo_recall.source = "demo"
    demo_recall.source_recall_id = "DEMO-TEST-001"
    item = InventoryItem(
        product_name="Fresh Valley Organic Spinach",
        brand="Fresh Valley",
        quantity=Decimal("12"),
        normalized_product_name=normalize_text("Fresh Valley Organic Spinach"),
        normalized_brand=normalize_brand("Fresh Valley"),
        raw_row={},
    )
    db_session.add_all([live_recall, demo_recall, item])
    await db_session.commit()

    result = await run_matching(db_session, min_score=0.35)

    assert result["created"] == 1
    assert await db_session.scalar(select(func.count(RecallMatch.id))) == 1
