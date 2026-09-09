from __future__ import annotations

from typing import Any

from app.db.models import InventoryItem, Recall
from app.seed.data import DEMO_COMPANY_PROFILES, SEED_RECALLS
from app.services.matching import score_recall_inventory
from app.services.text import normalize_brand, normalize_text

EXPECTED_PORTFOLIO_MATCHES = {
    ("DEMO-001", "Fresh Valley Organic Spinach"),
    ("DEMO-002", "Golden Grain Honey Oat Granola"),
    ("DEMO-003", "Harbor Catch Frozen Salmon Burgers"),
    ("DEMO-004", "Bright Dairy Vanilla Yogurt"),
    ("DEMO-005", "Casa Verde Mild Salsa"),
    ("DEMO-008", "Blue Kettle Creamy Peanut Butter"),
    ("DEMO-009", "Metro Market Chocolate Chip Muffins"),
    ("DEMO-010", "Evergreen Alfalfa Sprouts"),
}

MIN_PORTFOLIO_PRECISION = 0.95
MIN_PORTFOLIO_RECALL = 0.95
MIN_PORTFOLIO_HIGH_CONFIDENCE = 3
MIN_PORTFOLIO_MEDIUM_CONFIDENCE = 3


def _recall_from_seed(data: dict[str, Any]) -> Recall:
    return Recall(
        source="demo",
        source_recall_id=data["source_recall_id"],
        product_description=data["product_description"],
        brand_name=data["brand_name"],
        recalling_firm=data["recalling_firm"],
        classification=data["classification"],
        reason_for_recall=data["reason_for_recall"],
        distribution_pattern=data["distribution_pattern"],
        normalized_product_name=normalize_text(data["product_description"]),
        normalized_brand_name=normalize_brand(data["brand_name"]),
    )


def _item_from_seed(row: tuple[Any, ...]) -> InventoryItem:
    return InventoryItem(
        product_name=row[0],
        brand=row[1],
        upc=row[2] or None,
        lot_code=row[3] or None,
        normalized_product_name=normalize_text(row[0]),
        normalized_brand=normalize_brand(row[1]),
    )


def evaluate_portfolio_matching(min_score: float = 0.50) -> dict[str, Any]:
    if not 0 <= min_score <= 1:
        raise ValueError("min_score must be between 0 and 1")

    inventory_rows = DEMO_COMPANY_PROFILES[0]["items"]
    true_positives = false_positives = false_negatives = 0
    high_predictions = medium_predictions = 0
    predicted_count = 0

    for recall_data in SEED_RECALLS:
        recall = _recall_from_seed(recall_data)
        for inventory_row in inventory_rows:
            item = _item_from_seed(inventory_row)
            result = score_recall_inventory(recall, item)
            key = (recall.source_recall_id, item.product_name)
            expected = key in EXPECTED_PORTFOLIO_MATCHES
            predicted = result["score"] >= min_score
            if predicted:
                predicted_count += 1
                high_predictions += result["confidence"] == "high"
                medium_predictions += result["confidence"] == "medium"
            if predicted and expected:
                true_positives += 1
            elif predicted and not expected:
                false_positives += 1
            elif expected and not predicted:
                false_negatives += 1

    precision = true_positives / predicted_count if predicted_count else 0.0
    expected_count = len(EXPECTED_PORTFOLIO_MATCHES)
    recall = true_positives / expected_count if expected_count else 0.0
    return {
        "min_score": min_score,
        "total_cases": len(SEED_RECALLS) * len(inventory_rows),
        "expected_matches": expected_count,
        "predicted_matches": predicted_count,
        "true_positives": true_positives,
        "false_positives": false_positives,
        "false_negatives": false_negatives,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "high_confidence_predictions": high_predictions,
        "medium_confidence_predictions": medium_predictions,
    }


def portfolio_release_gate_failures(metrics: dict[str, Any]) -> list[str]:
    failures = []
    if metrics["precision"] < MIN_PORTFOLIO_PRECISION:
        failures.append(f"precision {metrics['precision']:.4f} < {MIN_PORTFOLIO_PRECISION:.2f}")
    if metrics["recall"] < MIN_PORTFOLIO_RECALL:
        failures.append(f"recall {metrics['recall']:.4f} < {MIN_PORTFOLIO_RECALL:.2f}")
    if metrics["high_confidence_predictions"] < MIN_PORTFOLIO_HIGH_CONFIDENCE:
        failures.append("high-confidence fixture count is below release threshold")
    if metrics["medium_confidence_predictions"] < MIN_PORTFOLIO_MEDIUM_CONFIDENCE:
        failures.append("medium-confidence fixture count is below release threshold")
    return failures
