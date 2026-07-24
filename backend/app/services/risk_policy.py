from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from app.db.models import InventoryItem, Recall


@dataclass(frozen=True)
class RiskPolicy:
    match_confidence: int = 35
    recall_class: int = 20
    lot_or_upc_exactness: int = 15
    quantity: int = 10
    location_criticality: int = 10
    supplier_overlap: int = 5
    review_status_pressure: int = 5


DEFAULT_POLICY = RiskPolicy()

CLASS_SCORES = {"class i": 1.0, "class ii": 0.65, "class iii": 0.3}
CRITICALITY_SCORES = {"critical": 1.0, "high": 0.85, "medium": 0.55, "low": 0.25, "storage": 0.15}
STATUS_SCORES = {"needs_review": 1.0, "confirmed": 0.8, "dismissed": 0.1, "resolved": 0.05}


def exposure_level_for_score(score: float) -> str:
    if score >= 85:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def _quantity_score(quantity: Decimal | None) -> float:
    if quantity is None:
        return 0.2
    amount = float(quantity)
    if amount >= 100:
        return 1.0
    if amount >= 50:
        return 0.8
    if amount >= 20:
        return 0.6
    if amount >= 5:
        return 0.35
    return 0.15


def _exactness_score(signals: list[dict[str, Any]]) -> float:
    exact_scores = [
        float(signal.get("score", 0))
        for signal in signals
        if signal.get("name") in {"upc_match", "lot_code_match"}
    ]
    return max(exact_scores, default=0.0)


def _supplier_score(recall: Recall, item: InventoryItem) -> float:
    supplier = (item.supplier or "").lower()
    firm = " ".join(filter(None, [recall.recalling_firm, recall.brand_name])).lower()
    if not supplier or not firm:
        return 0.2
    supplier_tokens = {token for token in supplier.replace(",", " ").split() if len(token) > 3}
    return 1.0 if supplier_tokens and any(token in firm for token in supplier_tokens) else 0.25


def calculate_exposure(
    recall: Recall,
    item: InventoryItem,
    match_score: float,
    signals: list[dict[str, Any]],
    status: str = "needs_review",
    policy: RiskPolicy = DEFAULT_POLICY,
) -> dict[str, Any]:
    class_key = (recall.classification or "").strip().lower()
    criticality_key = (item.location_criticality or item.location_type or "").strip().lower()
    public_boost = 0.15 if item.public_serving else 0.0
    location_score = min(1.0, CRITICALITY_SCORES.get(criticality_key, 0.45) + public_boost)
    factor_scores = {
        "match_confidence": match_score,
        "recall_class": CLASS_SCORES.get(class_key, 0.45),
        "lot_or_upc_exactness": _exactness_score(signals),
        "quantity": _quantity_score(item.quantity),
        "location_criticality": location_score,
        "supplier_overlap": _supplier_score(recall, item),
        "review_status_pressure": STATUS_SCORES.get(status, 0.5),
    }
    weights = policy.__dict__
    score = sum(factor_scores[name] * weights[name] for name in factor_scores)
    score = round(max(0.0, min(score, 100.0)), 2)
    return {
        "exposure_score": score,
        "exposure_level": exposure_level_for_score(score),
        "exposure_factors": {
            "weights": weights,
            "scores": {key: round(value, 3) for key, value in factor_scores.items()},
            "summary": build_exposure_summary(recall, item, score, factor_scores),
        },
    }


def build_exposure_summary(recall: Recall, item: InventoryItem, score: float, factors: dict[str, float]) -> str:
    reasons = []
    if factors["recall_class"] >= 0.9:
        reasons.append("Class I recall")
    if factors["lot_or_upc_exactness"] >= 0.9:
        reasons.append("exact lot or UPC evidence")
    if factors["location_criticality"] >= 0.75:
        reasons.append(f"{item.location_type or 'critical'} location")
    if factors["quantity"] >= 0.6:
        reasons.append("meaningful affected quantity")
    if not reasons:
        reasons.append("moderate match and operational context")
    return f"Exposure {score:.0f} because of " + ", ".join(reasons[:3]) + "."
