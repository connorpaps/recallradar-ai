import csv
import io
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.models import AuditEvent, InventoryItem, UploadedFile
from app.services.text import normalize_brand, normalize_text, parse_optional_date, parse_optional_decimal


def normalize_csv_key(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


async def import_inventory_csv(session: AsyncSession, filename: str, content: bytes) -> dict:
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Inventory CSV must be UTF-8 encoded") from exc

    reader = csv.DictReader(io.StringIO(decoded))
    fieldnames = {normalize_csv_key(name) for name in (reader.fieldnames or []) if name}
    if "product_name" not in fieldnames:
        raise ValueError("Inventory CSV must include a product_name column")

    settings = get_settings()
    rows: list[dict[str | None, Any]] = []
    for row in reader:
        if None in row:
            raise ValueError("Inventory CSV contains more values than its header")
        rows.append(row)
        if len(rows) > settings.max_csv_rows:
            raise ValueError(f"Inventory CSV cannot exceed {settings.max_csv_rows} rows")
    if not rows:
        raise ValueError("Inventory CSV must contain at least one data row")
    errors = []
    valid_rows = []
    upload = UploadedFile(
        file_type="inventory_csv",
        original_filename=filename,
        row_count=len(rows),
        status="processed",
    )
    session.add(upload)
    await session.flush()
    for index, raw_row in enumerate(rows, start=2):
        row = {
            normalize_csv_key(key): (value.strip() if isinstance(value, str) else value)
            for key, value in raw_row.items()
            if key
        }
        product_name = row.get("product_name")
        if not product_name:
            if len(errors) < settings.max_upload_errors:
                errors.append({"row": index, "message": "product_name is required"})
            continue
        purchase_date = parse_optional_date(row.get("purchase_date"))
        if row.get("purchase_date") and not purchase_date:
            if len(errors) < settings.max_upload_errors:
                errors.append({"row": index, "message": "purchase_date must use YYYY-MM-DD"})
            continue
        quantity = parse_optional_decimal(row.get("quantity"))
        if row.get("quantity") and quantity is None:
            if len(errors) < settings.max_upload_errors:
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
