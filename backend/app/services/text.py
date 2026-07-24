import re
from datetime import date
from decimal import Decimal, InvalidOperation

LEGAL_SUFFIXES = {"inc", "llc", "ltd", "co", "corp", "corporation", "company"}


def normalize_text(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    normalized = re.sub(r"\bounces?\b", "oz", normalized)
    normalized = re.sub(r"\bpounds?\b", "lb", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def normalize_brand(value: str | None) -> str:
    tokens = [token for token in normalize_text(value).split() if token not in LEGAL_SUFFIXES]
    return " ".join(tokens)


def parse_openfda_date(value: str | None) -> date | None:
    if not value or len(value) != 8:
        return None
    try:
        return date(int(value[0:4]), int(value[4:6]), int(value[6:8]))
    except ValueError:
        return None


def parse_optional_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def parse_optional_decimal(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(value.strip())
    except (InvalidOperation, AttributeError):
        return None


def summarize_recall(product: str, reason: str | None, classification: str | None) -> str:
    risk = classification or "Unclassified"
    reason_text = reason or "The source notice did not provide a detailed reason."
    return (
        f"{risk} recall involving {product}. Review local inventory for matching product names, "
        f"brands, UPCs, and lot codes. Reason: {reason_text}"
    )
