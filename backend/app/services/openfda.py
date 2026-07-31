import logging
from datetime import date, datetime, timedelta, timezone

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.ai.provider import ai_provider
from app.db.models import AuditEvent, ImportStatus, Recall
from app.services.model_runs import record_ai_result
from app.services.text import normalize_brand, normalize_text, parse_openfda_date, summarize_recall

logger = logging.getLogger(__name__)


def build_openfda_params(limit: int, since: date | None) -> dict[str, str | int]:
    params: dict[str, str | int] = {"limit": limit, "sort": "report_date:desc"}
    if since:
        compact_date = since.strftime("%Y%m%d")
        params["search"] = f"report_date:[{compact_date}+TO+99991231]"
    settings = get_settings()
    if settings.openfda_api_key:
        params["api_key"] = settings.openfda_api_key
    return params


async def fetch_openfda_recalls(limit: int, since: date | None) -> list[dict]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.get(settings.openfda_food_enforcement_url, params=build_openfda_params(limit, since))
        response.raise_for_status()
        payload = response.json()
        return payload.get("results", [])


def _as_aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


async def get_openfda_import_status(session: AsyncSession) -> ImportStatus:
    status = await session.get(ImportStatus, "openfda")
    if status:
        return status
    status = ImportStatus(source="openfda", status="idle")
    session.add(status)
    await session.commit()
    await session.refresh(status)
    return status


def should_refresh_openfda(status: ImportStatus) -> bool:
    last_success_at = _as_aware(status.last_success_at)
    if not last_success_at:
        return True
    refresh_after = timedelta(minutes=get_settings().openfda_refresh_minutes)
    return datetime.now(timezone.utc) - last_success_at >= refresh_after


def serialize_openfda_import_status(status: ImportStatus) -> dict:
    return {
        "source": status.source,
        "status": status.status,
        "imported": status.imported,
        "updated": status.updated,
        "skipped": status.skipped,
        "error": "The latest openFDA refresh failed." if status.error else None,
        "last_attempt_at": status.last_attempt_at,
        "last_success_at": status.last_success_at,
        "refresh_after_minutes": get_settings().openfda_refresh_minutes,
        "should_refresh": should_refresh_openfda(status),
    }


async def import_openfda_recalls(session: AsyncSession, limit: int, since: date | None, force: bool = True) -> dict[str, int | str | bool]:
    status = await get_openfda_import_status(session)
    if not force and not should_refresh_openfda(status):
        return {"imported": 0, "updated": 0, "skipped": 0, "status": status.status, "refreshed": False}
    status.status = "running"
    status.error = None
    status.last_attempt_at = datetime.now(timezone.utc)
    await session.commit()

    imported = 0
    updated = 0
    skipped = 0
    try:
        records = await fetch_openfda_recalls(limit, since)
    except Exception as exc:
        logger.exception("openFDA import failed")
        status.status = "failed"
        status.error = "openFDA refresh failed"
        status.last_attempt_at = datetime.now(timezone.utc)
        await session.commit()
        raise
    for record in records:
        source_id = record.get("recall_number") or record.get("event_id")
        product_description = record.get("product_description")
        if not source_id or not product_description:
            skipped += 1
            continue
        existing = await session.scalar(
            select(Recall).where(Recall.source == "openfda", Recall.source_recall_id == source_id)
        )
        deterministic_summary = summarize_recall(product_description, record.get("reason_for_recall"), record.get("classification"))
        summary_result = await ai_provider.summarize(
            " ".join(
                filter(
                    None,
                    [
                        f"Classification: {record.get('classification')}",
                        f"Product: {product_description}",
                        f"Reason: {record.get('reason_for_recall')}",
                        f"Distribution: {record.get('distribution_pattern')}",
                    ],
                )
            )
        )
        values = {
            "source_url": "https://open.fda.gov/apis/food/enforcement/",
            "status": record.get("status"),
            "classification": record.get("classification"),
            "product_description": product_description,
            "brand_name": record.get("brand_name"),
            "recalling_firm": record.get("recalling_firm"),
            "reason_for_recall": record.get("reason_for_recall"),
            "distribution_pattern": record.get("distribution_pattern"),
            "recall_initiation_date": parse_openfda_date(record.get("recall_initiation_date")),
            "report_date": parse_openfda_date(record.get("report_date")),
            "termination_date": parse_openfda_date(record.get("termination_date")),
            "normalized_product_name": normalize_text(product_description),
            "normalized_brand_name": normalize_brand(record.get("brand_name") or record.get("recalling_firm")),
            "summary": str(summary_result.value) if summary_result.value else deterministic_summary,
            "raw_payload": record,
        }
        if existing:
            for key, value in values.items():
                setattr(existing, key, value)
            await record_ai_result(
                session,
                summary_result,
                "recall_summary",
                "recall",
                existing.id,
                "recall",
                existing.id,
                {"source": "openfda", "updated": True},
            )
            updated += 1
            continue
        recall = Recall(source="openfda", source_recall_id=source_id, **values)
        session.add(recall)
        await session.flush()
        await record_ai_result(
            session,
            summary_result,
            "recall_summary",
            "recall",
            recall.id,
            "recall",
            recall.id,
            {"source": "openfda", "updated": False},
        )
        session.add(
            AuditEvent(
                entity_type="recall",
                entity_id=recall.id,
                event_type="recall.imported",
                actor_type="system",
                metadata_={"source": "openfda"},
            )
        )
        imported += 1
    status.status = "succeeded"
    status.imported = imported
    status.updated = updated
    status.skipped = skipped
    status.error = None
    status.last_success_at = datetime.now(timezone.utc)
    await session.commit()
    return {"imported": imported, "updated": updated, "skipped": skipped, "status": "succeeded", "refreshed": True}
