import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import RecallMatch
from app.db.models import Recall
from app.db.session import get_session
from app.schemas import MatchList, MatchRunRequest, MatchRunResponse, MatchStatusRequest, MatchStatusResponse, RecallMatchOut
from app.services.matching import get_match_with_relations, run_matching, update_match_status

router = APIRouter(prefix="/matches", tags=["matches"])


@router.post("/run", response_model=MatchRunResponse)
async def run_match_job(
    request: MatchRunRequest,
    session: AsyncSession = Depends(get_session),
) -> MatchRunResponse:
    result = await run_matching(session, request.recall_id, request.inventory_upload_id, request.min_score, request.recall_source)
    return MatchRunResponse(**result)


@router.get("", response_model=MatchList)
async def list_matches(
    status: str | None = None,
    confidence: str | None = None,
    recall_source: str | None = "openfda",
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> MatchList:
    query = select(RecallMatch).options(selectinload(RecallMatch.inventory_item), selectinload(RecallMatch.recall))
    if recall_source:
        query = query.join(RecallMatch.recall).where(Recall.source == recall_source)
    if status:
        query = query.where(RecallMatch.status == status)
    if confidence:
        query = query.where(RecallMatch.confidence == confidence)
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = (await session.scalars(
        query.order_by(RecallMatch.exposure_score.desc(), RecallMatch.score.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )).all()
    return MatchList(items=[RecallMatchOut.model_validate(row) for row in rows], page=page, page_size=page_size, total=total or 0)


@router.get("/{match_id}", response_model=RecallMatchOut)
async def get_match(match_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> RecallMatchOut:
    match = await get_match_with_relations(session, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    return RecallMatchOut.model_validate(match)


@router.patch("/{match_id}/status", response_model=MatchStatusResponse)
async def patch_match_status(
    match_id: uuid.UUID,
    request: MatchStatusRequest,
    session: AsyncSession = Depends(get_session),
) -> MatchStatusResponse:
    try:
        match = await update_match_status(session, match_id, request.status, request.note, request.reviewer_name)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return MatchStatusResponse(id=match.id, status=match.status, reviewed_at=match.reviewed_at)
