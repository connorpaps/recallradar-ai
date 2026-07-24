from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent
from app.db.session import get_session
from app.schemas import AuditEventOut

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("")
async def list_audit_events(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
) -> dict:
    rows = (
        await session.scalars(select(AuditEvent).order_by(AuditEvent.created_at.desc()).offset((page - 1) * page_size).limit(page_size))
    ).all()
    return {"items": [AuditEventOut.model_validate(row) for row in rows], "page": page, "page_size": page_size}
