import csv
import io
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEvent, InventoryItem, UploadedFile
from app.services.text import normalize_brand, normalize_text, parse_optional_date, parse_optional_decimal


def normalize_csv_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


async def import_inventory_csv(session: AsyncSession, filename: str, content: bytes) -> dict:
    decoded = content.decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(decoded))
    errors = []
    valid_rows = []
    rows = list(reader)
    upload = UploadedFile(
        file_type="inventory_csv",
        original_filename=filename,
        row_count=len(rows),
        status="processed",
    )
    session.add(upload)
    await session.flush()
    for index, raw_row in enumerate(rows, start=2):
        row = {normalize_csv_key(key): (value.strip() if isinstance(value, str) else value) for key, value in raw_row.items()}
        product_name = row.get("product_name")
        if not product_name:
            errors.append({"row": index, "message": "product_name is required"})
            continue
        purchase_date = parse_optional_date(row.get("purchase_date"))
        if row.get("purchase_date") and not purchase_date:
            errors.append({"row": index, "message": "purchase_date must use YYYY-MM-DD"})
            continue
        quantity = parse_optional_decimal(row.get("quantity"))
        if row.get("quantity") and quantity is None:
            errors.append({"row": index, "message": "quantity must be a number"})
            continue
        item = InventoryItem(
            product_name=product_name,
            brand=row.get("brand") or None,
            upc=row.get("upc") or None,
            lot_code=row.get("lot_code") or None,
            quantity=quantity,
            unit=row.get("unit") or "units",
            location=row.get("location") or None,
            location_type=row.get("location_type") or None,
            location_criticality=row.get("location_criticality") or None,
            public_serving=(row.get("public_serving") or "").lower() in {"true", "yes", "1", "y"},
            region=row.get("region") or None,
            supplier=row.get("supplier") or None,
            purchase_date=purchase_date,
            normalized_product_name=normalize_text(product_name),
            normalized_brand=normalize_brand(row.get("brand")),
            uploaded_file_id=upload.id,
            raw_row=row,
        )
        valid_rows.append(item)
        session.add(item)
    upload.valid_row_count = len(valid_rows)
    upload.invalid_row_count = len(errors)
    upload.error_summary = f"{len(errors)} rows failed validation" if errors else None
    await session.flush()
    session.add(
        AuditEvent(
            entity_type="uploaded_file",
            entity_id=upload.id,
            event_type="inventory.uploaded",
            actor_type="user",
            actor_label="Demo User",
            metadata_={"filename": filename, "valid_rows": len(valid_rows), "invalid_rows": len(errors)},
        )
    )
    await session.commit()
    return {
        "uploaded_file_id": upload.id,
        "row_count": len(rows),
        "valid_row_count": len(valid_rows),
        "invalid_row_count": len(errors),
        "errors": errors,
    }
