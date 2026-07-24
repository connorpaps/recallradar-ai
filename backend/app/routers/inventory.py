import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import InventoryItem
from app.db.session import get_session
from app.schemas import DemoCompanyOut, InventoryItemOut, InventoryUploadResponse, SeedCompanyRequest, SeedCompanyResponse, SeedSummary
from app.services.inventory import import_inventory_csv
from app.services.seed import list_demo_companies, seed_company_inventory, seed_inventory

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.post("/seed", response_model=SeedSummary)
async def seed_inventory_records(session: AsyncSession = Depends(get_session)) -> SeedSummary:
    return SeedSummary(created=await seed_inventory(session))


@router.get("/demo-companies", response_model=list[DemoCompanyOut])
async def get_demo_companies() -> list[DemoCompanyOut]:
    return [DemoCompanyOut(**company) for company in list_demo_companies()]


@router.post("/seed-company", response_model=SeedCompanyResponse)
async def seed_demo_company_inventory(
    request: SeedCompanyRequest,
    session: AsyncSession = Depends(get_session),
) -> SeedCompanyResponse:
    try:
        result = await seed_company_inventory(session, request.company_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return SeedCompanyResponse(**result)


@router.post("/upload", response_model=InventoryUploadResponse)
async def upload_inventory(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
) -> InventoryUploadResponse:
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Inventory upload must be a CSV file")
    content = await file.read()
    result = await import_inventory_csv(session, file.filename, content)
    return InventoryUploadResponse(**result)


@router.get("")
async def list_inventory(
    q: str | None = None,
    active: bool = True,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=200),
    session: AsyncSession = Depends(get_session),
) -> dict:
    query = select(InventoryItem).where(InventoryItem.active == active)
    if q:
        pattern = f"%{q}%"
        query = query.where(or_(InventoryItem.product_name.ilike(pattern), InventoryItem.brand.ilike(pattern)))
    total = await session.scalar(select(func.count()).select_from(query.subquery()))
    rows = (
        await session.scalars(
            query.order_by(InventoryItem.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        )
    ).all()
    return {"items": [InventoryItemOut.model_validate(row) for row in rows], "page": page, "page_size": page_size, "total": total or 0}


@router.get("/{inventory_item_id}", response_model=InventoryItemOut)
async def get_inventory_item(inventory_item_id: uuid.UUID, session: AsyncSession = Depends(get_session)) -> InventoryItemOut:
    item = await session.scalar(select(InventoryItem).where(InventoryItem.id == inventory_item_id))
    if not item:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return InventoryItemOut.model_validate(item)
