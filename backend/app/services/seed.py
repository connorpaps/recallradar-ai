from decimal import Decimal

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent, InventoryItem, Recall, RecallMatch, UploadedFile
from app.ai.provider import ai_provider
from app.seed.data import BASE_INVENTORY, DEMO_COMPANY_PROFILES, FILLER_PRODUCTS, SEED_RECALLS
from app.services.model_runs import record_ai_result
from app.services.text import normalize_brand, normalize_text, parse_openfda_date, summarize_recall


async def seed_recalls(session: AsyncSession) -> int:
    created = 0
    for item in SEED_RECALLS:
        exists = await session.scalar(
            select(Recall).where(Recall.source == "demo", Recall.source_recall_id == item["source_recall_id"])
        )
        if exists:
            continue
        deterministic_summary = summarize_recall(item["product_description"], item["reason_for_recall"], item["classification"])
        summary_result = await ai_provider.summarize(
            f"{item['classification']} recall. Product: {item['product_description']}. Reason: {item['reason_for_recall']}"
        )
        recall = Recall(
            source="demo",
            source_recall_id=item["source_recall_id"],
            source_url="https://open.fda.gov/apis/food/enforcement/",
            status="Ongoing",
            classification=item["classification"],
            product_description=item["product_description"],
            brand_name=item["brand_name"],
            recalling_firm=item["recalling_firm"],
            reason_for_recall=item["reason_for_recall"],
            distribution_pattern=item["distribution_pattern"],
            recall_initiation_date=parse_openfda_date(item["recall_initiation_date"].replace("-", "")),
            report_date=parse_openfda_date(item["recall_initiation_date"].replace("-", "")),
            normalized_product_name=normalize_text(item["product_description"]),
            normalized_brand_name=normalize_brand(item["brand_name"]),
            summary=str(summary_result.value) if summary_result.value else deterministic_summary,
            raw_payload=item,
        )
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
            {"source": "demo"},
        )
        created += 1
    await session.commit()
    return created


def list_demo_companies() -> list[dict]:
    return [
        {
            "id": profile["id"],
            "name": profile["name"],
            "company_type": profile["company_type"],
            "description": profile["description"],
            "risk_context": profile["risk_context"],
            "item_count": len(profile["items"]),
            "recommended": profile.get("recommended", False),
        }
        for profile in DEMO_COMPANY_PROFILES
    ]


def get_demo_company(company_id: str) -> dict:
    for profile in DEMO_COMPANY_PROFILES:
        if profile["id"] == company_id:
            return profile
    raise LookupError("Demo company not found")


async def clear_inventory_and_matches(session: AsyncSession) -> None:
    await session.execute(delete(RecallMatch))
    await session.execute(delete(InventoryItem))
    await session.execute(delete(UploadedFile))
    await session.commit()


async def seed_company_inventory(session: AsyncSession, company_id: str = "metro_mart_grocery") -> dict:
    profile = get_demo_company(company_id)
    await clear_inventory_and_matches(session)
    upload = UploadedFile(
        file_type="demo_company_inventory",
        original_filename=f"{company_id}.csv",
        row_count=len(profile["items"]),
        valid_row_count=len(profile["items"]),
        invalid_row_count=0,
        status="processed",
    )
    session.add(upload)
    await session.flush()
    created = 0
    for idx, row in enumerate(profile["items"]):
        (
            product_name,
            brand,
            upc,
            lot_code,
            quantity,
            location,
            location_type,
            location_criticality,
            public_serving,
            region,
            supplier,
        ) = row
        item = InventoryItem(
            product_name=product_name,
            brand=brand,
            upc=upc or None,
            lot_code=lot_code,
            quantity=Decimal(quantity),
            unit="units",
            location=location,
            location_type=location_type,
            location_criticality=location_criticality,
            public_serving=public_serving,
            region=region,
            supplier=supplier,
            normalized_product_name=normalize_text(product_name),
            normalized_brand=normalize_brand(brand),
            uploaded_file_id=upload.id,
            raw_row={
                "demo_row": idx + 1,
                "demo_company_id": profile["id"],
                "demo_company_name": profile["name"],
                "inventory_source": "demo_company",
            },
        )
        session.add(item)
        created += 1
    session.add(
        AuditEvent(
            entity_type="inventory",
            entity_id=upload.id,
            event_type="inventory.demo_company_loaded",
            actor_type="system",
            actor_label=profile["name"],
            metadata_={"demo_company_id": profile["id"], "demo_company_name": profile["name"], "created": created},
        )
    )
    await session.commit()
    return {"created": created, "company": list_demo_company(profile)}


def list_demo_company(profile: dict) -> dict:
    return {
        "id": profile["id"],
        "name": profile["name"],
        "company_type": profile["company_type"],
        "description": profile["description"],
        "risk_context": profile["risk_context"],
        "item_count": len(profile["items"]),
        "recommended": profile.get("recommended", False),
    }


async def seed_inventory(session: AsyncSession) -> int:
    return (await seed_company_inventory(session, "metro_mart_grocery"))["created"]


async def seed_legacy_inventory(session: AsyncSession) -> int:
    upload = UploadedFile(
        file_type="inventory_csv",
        original_filename="demo_inventory.csv",
        row_count=len(BASE_INVENTORY) + len(FILLER_PRODUCTS),
        valid_row_count=len(BASE_INVENTORY) + len(FILLER_PRODUCTS),
        invalid_row_count=0,
        status="processed",
    )
    session.add(upload)
    await session.flush()
    created = 0
    for idx, row in enumerate(BASE_INVENTORY):
        (
            product_name,
            brand,
            upc,
            lot_code,
            quantity,
            location,
            location_type,
            location_criticality,
            public_serving,
            region,
            supplier,
        ) = row
        item = InventoryItem(
            product_name=product_name,
            brand=brand,
            upc=upc or None,
            lot_code=lot_code,
            quantity=Decimal(quantity),
            unit="units",
            location=location,
            location_type=location_type,
            location_criticality=location_criticality,
            public_serving=public_serving,
            region=region,
            supplier=supplier,
            normalized_product_name=normalize_text(product_name),
            normalized_brand=normalize_brand(brand),
            uploaded_file_id=upload.id,
            raw_row={"demo_row": idx + 1},
        )
        session.add(item)
        created += 1
    for idx, product_name in enumerate(FILLER_PRODUCTS):
        brand = product_name.split()[0] + " " + product_name.split()[1]
        item = InventoryItem(
            product_name=product_name,
            brand=brand,
            quantity=Decimal((idx % 18) + 3),
            unit="units",
            location=f"Warehouse - Dry Storage {(idx % 8) + 1}",
            location_type="storage",
            location_criticality="storage",
            public_serving=False,
            region="Northeast",
            supplier="Demo Distributor",
            normalized_product_name=normalize_text(product_name),
            normalized_brand=normalize_brand(brand),
            uploaded_file_id=upload.id,
            raw_row={"demo_row": idx + len(BASE_INVENTORY) + 1},
        )
        session.add(item)
        created += 1
    await session.commit()
    return created


async def reset_demo_data(session: AsyncSession) -> None:
    await session.execute(delete(RecallMatch))
    await session.execute(delete(InventoryItem))
    await session.execute(delete(UploadedFile))
    await session.execute(delete(Recall).where(Recall.source == "demo"))
    await session.execute(delete(AuditEvent))
    await session.commit()
