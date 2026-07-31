import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import AuditEvent, Recall, RecallMatch
from app.db.session import get_session
from app.schemas import ImportOpenFdaRequest, ImportStatusOut, ImportSummary, PaginatedRecalls, RecallDetail, RecallListItem, RecallMatchOut, SeedSummary
from app.config import get_settings
from app.services.openfda import get_openfda_import_status, import_openfda_recalls, serialize_openfda_import_status
from app.services.seed import seed_recalls

router = APIRouter(prefix="/recalls", tags=["recalls"])


@router.post("/seed", response_model=SeedSummary)
async def seed_recall_records(session: AsyncSession = Depends(get_session)) -> SeedSummary:
    if not get_settings().enable_demo_recall_seed:
        raise HTTPException(status_code=404, detail="Demo recall seeding is disabled")
    return SeedSummary(created=await seed_recalls(session))


@router.post("/import/openfda", response_model=ImportSummary)
async def import_recalls(
    request: ImportOpenFdaRequest,
    session: AsyncSession = Depends(get_session),
) -> ImportSummary:
    try:
        result = await import_openfda_recalls(session, request.limit, request.since, request.force)
    except Exception as exc:
        raise HTTPException(status_code=502, detail="openFDA import failed. Please try again later.") from exc
    return ImportSummary(**result)


@router.get("/imports/status", response_model=ImportStatusOut)
async def get_import_status(session: AsyncSession = Depends(get_session)) -> ImportStatusOut:
    status = await get_openfda_import_status(session)
    return ImportStatusOut(**serialize_openfda_import_status(status))


@router.get("", response_model=PaginatedRecalls)
async def list_recalls(
    q: str | None = None,
    source: str | None = None,
    classification: str | None = None,
    has_matches: bool | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> PaginatedRecalls:
    settings = get_settings()
    query = select(Recall)
    if source:
        if source == "live":
            query = query.where(Recall.source == "openfda")
        elif source == "demo":
            if not settings.enable_demo_recall_seed:
                query = query.where(Recall.source == "openfda")
            else:
                query = query.where(Recall.source == "demo")
        else:
            query = query.where(Recall.source == source)
    else:
        query = query.where(Recall.source == "openfda")
    if q:
        pattern = f"%{q}%"
        query = query.where(
            or_(
                Recall.product_description.ilike(pattern),
                Recall.brand_name.ilike(pattern),
                Recall.recalling_firm.ilike(pattern),
                Recall.reason_for_recall.ilike(pattern),
            )
        )
    if classification:
        query = query.where(Recall.classification == classification)
    if has_matches is True:
        query = query.join(RecallMatch).distinct()
    if has_matches is False:
        query = query.outerjoin(RecallMatch).where(RecallMatch.id.is_(None))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = (
        await session.scalars(
            query.order_by(Recall.recall_initiation_date.desc().nullslast()).offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    items = []
    for recall in rows:
        match_count = await session.scalar(select(func.count(RecallMatch.id)).where(RecallMatch.recall_id == recall.id))
        highest_confidence = await session.scalar(
            select(RecallMatch.confidence)
            .where(RecallMatch.recall_id == recall.id)
            .order_by(RecallMatch.score.desc())
            .limit(1)
        )
        items.append(
            RecallListItem.model_validate(
                {**recall.__dict__, "match_count": match_count or 0, "highest_confidence": highest_confidence}
            )
        )
    return PaginatedRecalls(items=items, page=page, page_size=page_size, total=total or 0)


@router.get("/{recall_id}", response_model=RecallDetail)
async def get_recall(recall_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> RecallDetail:
    recall = await session.scalar(select(Recall).where(Recall.id == recall_id))
    if not recall:
        raise HTTPException(status_code=404, detail="Recall not found")
    match_count = await session.scalar(select(func.count(RecallMatch.id)).where(RecallMatch.recall_id == recall.id))
    audit_events = (
        await session.scalars(
            select(AuditEvent)
            .where(AuditEvent.entity_id == recall.id)
            .order_by(AuditEvent.created_at.desc())
            .limit(20)
        )
    ).all()
    return RecallDetail.model_validate({**recall.__dict__, "match_count": match_count or 0, "audit_events": audit_events})


@router.get("/{recall_id}/matches")
async def get_recall_matches(recall_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> dict:
    matches = (
        await session.scalars(
            select(RecallMatch)
            .options(selectinload(RecallMatch.inventory_item), selectinload(RecallMatch.recall))
            .where(RecallMatch.recall_id == recall_id)
            .order_by(RecallMatch.score.desc())
        )
    ).all()
    return {"items": [RecallMatchOut.model_validate(match) for match in matches]}
