from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import AuditEvent, InventoryItem, Recall, RecallMatch
from app.db.session import get_session
from app.schemas import DashboardSummary, RecallMatchOut

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


async def count_grouped(session: AsyncSession, column) -> dict[str, int]:
    rows = (await session.execute(select(column, func.count()).group_by(column))).all()
    return {key: count for key, count in rows}


async def count_grouped_live_matches(session: AsyncSession, column) -> dict[str, int]:
    rows = (
        await session.execute(
            select(column, func.count())
            .select_from(RecallMatch)
            .join(RecallMatch.recall)
            .where(Recall.source == "openfda")
            .group_by(column)
        )
    ).all()
    return {key: count for key, count in rows}


async def top_grouped_exposure(session: AsyncSession, column) -> list[dict]:
    rows = (
        await session.execute(
            select(column, func.count(RecallMatch.id), func.max(RecallMatch.exposure_score))
            .join(RecallMatch.inventory_item)
            .join(RecallMatch.recall)
            .where(RecallMatch.status == "needs_review")
            .where(Recall.source == "openfda")
            .group_by(column)
            .order_by(func.max(RecallMatch.exposure_score).desc())
            .limit(5)
        )
    ).all()
    return [
        {"label": label or "Unassigned", "count": count, "max_exposure_score": float(max_score or 0)}
        for label, count, max_score in rows
    ]


async def current_inventory_company(session: AsyncSession) -> dict | None:
    rows = (
        await session.execute(
            select(InventoryItem.raw_row).where(InventoryItem.raw_row["inventory_source"].as_string() == "demo_company")
        )
    ).all()
    if not rows:
        return None
    raw_row = rows[0][0]
    return {
        "id": raw_row.get("demo_company_id"),
        "name": raw_row.get("demo_company_name"),
        "inventory_source": raw_row.get("inventory_source"),
        "item_count": len(rows),
    }


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(session: AsyncSession = Depends(get_session)) -> DashboardSummary:
    active_recalls = await session.scalar(select(func.count(Recall.id)).where(Recall.source == "openfda"))
    inventory_items = await session.scalar(select(func.count(InventoryItem.id)).where(InventoryItem.active.is_(True)))
    matches_needing_review = await session.scalar(
        select(func.count(RecallMatch.id)).join(RecallMatch.recall).where(Recall.source == "openfda").where(RecallMatch.status == "needs_review")
    )
    high_confidence_matches = await session.scalar(
        select(func.count(RecallMatch.id)).join(RecallMatch.recall).where(Recall.source == "openfda").where(RecallMatch.confidence == "high")
    )
    recent_activity = (
        await session.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).limit(8))
    ).all()
    high_risk_matches = (
        await session.scalars(
            select(RecallMatch)
            .options(selectinload(RecallMatch.inventory_item), selectinload(RecallMatch.recall))
            .join(RecallMatch.recall)
            .where(Recall.source == "openfda")
            .where(RecallMatch.status == "needs_review")
            .order_by(RecallMatch.exposure_score.desc(), RecallMatch.score.desc())
            .limit(5)
        )
    ).all()
    return DashboardSummary(
        active_recalls=active_recalls or 0,
        inventory_items=inventory_items or 0,
        matches_needing_review=matches_needing_review or 0,
        high_confidence_matches=high_confidence_matches or 0,
        matches_by_status=await count_grouped_live_matches(session, RecallMatch.status),
        matches_by_confidence=await count_grouped_live_matches(session, RecallMatch.confidence),
        matches_by_exposure=await count_grouped_live_matches(session, RecallMatch.exposure_level),
        recall_source_counts={"openfda": active_recalls or 0},
        current_inventory_company=await current_inventory_company(session),
        top_exposed_locations=await top_grouped_exposure(session, InventoryItem.location),
        top_exposed_suppliers=await top_grouped_exposure(session, InventoryItem.supplier),
        recent_activity=recent_activity,
        high_risk_matches=[RecallMatchOut.model_validate(match) for match in high_risk_matches],
    )
