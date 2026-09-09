from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_session
from app.schemas import PortfolioDemoResponse
from app.services.seed import seed_portfolio_demo

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/portfolio", response_model=PortfolioDemoResponse)
async def load_portfolio_demo(
    session: AsyncSession = Depends(get_session),
) -> PortfolioDemoResponse:
    if not get_settings().enable_portfolio_demo:
        raise HTTPException(status_code=404, detail="Portfolio Demo is disabled")
    try:
        result = await seed_portfolio_demo(session)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return PortfolioDemoResponse(**result)
