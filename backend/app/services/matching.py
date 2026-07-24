from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from rapidfuzz import fuzz
from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.ai.provider import ai_provider
from app.db.models import AuditEvent, HumanReview, InventoryItem, Recall, RecallMatch
from app.services.model_runs import record_ai_result
from app.services.risk_policy import calculate_exposure
from app.services.text import normalize_brand, normalize_text


@dataclass
class Signal:
    name: str
    score: float
    weight: float
    detail: str
    matched_values: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "score": round(self.score, 4),
            "weight": self.weight,
            "detail": self.detail,
            "matched_values": self.matched_values,
        }


def fuzzy_score(left: str, right: str) -> float:
    if not left or not right:
        return 0
    token_score = fuzz.token_set_ratio(left, right) / 100
    partial_score = fuzz.partial_ratio(left, right) / 100
    return max(token_score, partial_score)


def confidence_for_score(score: float) -> str:
    if score >= 0.75:
        return "high"
    if score >= 0.5:
        return "medium"
    return "low"


def score_recall_inventory(recall: Recall, item: InventoryItem) -> dict[str, Any]:
    recall_product = recall.normalized_product_name or normalize_text(recall.product_description)
    item_product = item.normalized_product_name or normalize_text(item.product_name)
    recall_brand = recall.normalized_brand_name or normalize_brand(recall.brand_name or recall.recalling_firm)
    item_brand = item.normalized_brand or normalize_brand(item.brand)
    product_score = fuzzy_score(recall_product, item_product)
    brand_score = fuzzy_score(recall_brand, item_brand)
    upc_score = 0.0
    lot_score = 0.0
    distribution_score = 0.3
    signals = [
        Signal(
            "product_similarity",
            product_score,
            0.35,
            "Product descriptions are similar." if product_score > 0.65 else "Product descriptions have limited overlap.",
            {"recall": recall.product_description, "inventory": item.product_name},
        ),
        Signal(
            "brand_similarity",
            brand_score,
            0.25,
            "Brand or firm names are similar." if brand_score > 0.65 else "Brand evidence is weak or unavailable.",
            {"recall": recall.brand_name or recall.recalling_firm, "inventory": item.brand},
        ),
    ]
    if item.upc and item.upc in recall_product:
        upc_score = 1.0
    signals.append(
        Signal(
            "upc_match",
            upc_score,
            0.20,
            "Exact UPC evidence found." if upc_score else "UPC evidence is unavailable in the recall text.",
            {"recall": recall.product_description, "inventory": item.upc},
        )
    )
    if item.lot_code and normalize_text(item.lot_code) in recall_product:
        lot_score = 1.0
    signals.append(
        Signal(
            "lot_code_match",
            lot_score,
            0.15,
            "Lot code evidence found." if lot_score else "Lot code evidence is unavailable or does not match.",
            {"recall": recall.product_description, "inventory": item.lot_code},
        )
    )
    distribution = normalize_text(recall.distribution_pattern)
    if "nationwide" in distribution or "united states" in distribution:
        distribution_score = 1.0
    elif item.location and any(token in distribution for token in ("new york", "ny", "northeastern")):
        distribution_score = 0.8
    signals.append(
        Signal(
            "distribution_relevance",
            distribution_score,
            0.05,
            "Distribution does not rule this item out." if distribution_score >= 0.5 else "Distribution evidence is limited.",
            {"recall": recall.distribution_pattern, "inventory": item.location},
        )
    )
    score = sum(signal.score * signal.weight for signal in signals)
    if item.upc and upc_score == 1:
        score += 0.15
    if item.lot_code and lot_score == 1:
        score += 0.15
    if product_score > 0.78 and brand_score > 0.78:
        score += 0.10
    score = max(0.0, min(score, 1.0))
    explanation = build_explanation(recall, item, score, signals)
    signal_dicts = [signal.to_dict() for signal in signals]
    exposure = calculate_exposure(recall, item, score, signal_dicts)
    return {
        "score": score,
        "confidence": confidence_for_score(score),
        "signals": signal_dicts,
        "explanation": explanation,
        **exposure,
        "matched_fields": {
            "recall_product": recall.product_description,
            "inventory_product": item.product_name,
            "recall_brand": recall.brand_name or recall.recalling_firm,
            "inventory_brand": item.brand,
        },
    }


async def score_recall_inventory_with_ai(session: AsyncSession, recall: Recall, item: InventoryItem) -> dict[str, Any]:
    result = score_recall_inventory(recall, item)
    semantic = await ai_provider.semantic_similarity(
        f"{recall.product_description} {recall.reason_for_recall or ''}",
        f"{item.product_name} {item.brand or ''} {item.supplier or ''}",
    )
    await record_ai_result(
        session,
        semantic,
        "semantic_similarity",
        "recall",
        recall.id,
        "inventory_item",
        item.id,
        {"recall_id": str(recall.id), "inventory_item_id": str(item.id)},
    )
    if semantic.value is None:
        return result
    semantic_score = float(semantic.value)
    signal = Signal(
        "semantic_similarity",
        semantic_score,
        0.10,
        "Hugging Face semantic similarity supports this match." if semantic_score >= 0.65 else "Semantic similarity is weak.",
        {"recall": recall.product_description, "inventory": item.product_name},
    ).to_dict()
    result["signals"].append(signal)
    if semantic_score >= 0.55:
        result["score"] = max(0.0, min(result["score"] + (semantic_score * 0.10), 1.0))
        result["confidence"] = confidence_for_score(result["score"])
        result["explanation"] = (
            result["explanation"]
            + f" Semantic model signal: {semantic_score:.2f}, used as supporting evidence only."
        )
    exposure = calculate_exposure(recall, item, result["score"], result["signals"])
    result.update(exposure)
    return result


def build_explanation(recall: Recall, item: InventoryItem, score: float, signals: list[Signal]) -> str:
    strong = [signal.detail for signal in signals if signal.score >= 0.75]
    if strong:
        reason = " ".join(strong[:2])
    else:
        reason = "The match is based on partial product, brand, or distribution evidence."
    return (
        f"{item.product_name} may match the recall for {recall.product_description}. "
        f"{reason} Confidence score: {score:.2f}. Human review is required before action."
    )


async def run_matching(
    session: AsyncSession,
    recall_id: Any | None = None,
    inventory_upload_id: Any | None = None,
    min_score: float = 0.35,
    recall_source: str | None = "openfda",
) -> dict[str, int]:
    recall_query = select(Recall)
    inventory_query = select(InventoryItem).where(InventoryItem.active.is_(True))
    if recall_id:
        recall_query = recall_query.where(Recall.id == recall_id)
    elif recall_source:
        recall_query = recall_query.where(Recall.source == recall_source)
    if inventory_upload_id:
        inventory_query = inventory_query.where(InventoryItem.uploaded_file_id == inventory_upload_id)
    recalls = (await session.scalars(recall_query)).all()
    items = (await session.scalars(inventory_query)).all()
    created = 0
    updated = 0
    skipped = 0
    for recall in recalls:
        for item in items:
            result = await score_recall_inventory_with_ai(session, recall, item)
            if result["score"] < min_score:
                skipped += 1
                continue
            existing = await session.scalar(
                select(RecallMatch).where(
                    and_(RecallMatch.recall_id == recall.id, RecallMatch.inventory_item_id == item.id)
                )
            )
            if existing:
                existing.score = Decimal(str(round(result["score"], 4)))
                existing.confidence = result["confidence"]
                existing.signals = result["signals"]
                existing.explanation = result["explanation"]
                existing.exposure_score = Decimal(str(result["exposure_score"]))
                existing.exposure_level = result["exposure_level"]
                existing.exposure_factors = result["exposure_factors"]
                existing.matched_fields = result["matched_fields"]
                updated += 1
                continue
            match = RecallMatch(
                recall_id=recall.id,
                inventory_item_id=item.id,
                score=Decimal(str(round(result["score"], 4))),
                confidence=result["confidence"],
                signals=result["signals"],
                explanation=result["explanation"],
                exposure_score=Decimal(str(result["exposure_score"])),
                exposure_level=result["exposure_level"],
                exposure_factors=result["exposure_factors"],
                matched_fields=result["matched_fields"],
            )
            session.add(match)
            await session.flush()
            session.add(
                AuditEvent(
                    entity_type="recall_match",
                    entity_id=match.id,
                    event_type="match.generated",
                    actor_type="system",
                    metadata_={
                        "score": result["score"],
                        "confidence": result["confidence"],
                        "exposure_score": result["exposure_score"],
                        "exposure_level": result["exposure_level"],
                    },
                )
            )
            created += 1
    await session.commit()
    return {"created": created, "updated": updated, "skipped": skipped}


async def update_match_status(
    session: AsyncSession,
    match_id: Any,
    status: str,
    note: str | None,
    reviewer_name: str | None,
) -> RecallMatch:
    if status not in {"needs_review", "confirmed", "dismissed", "resolved"}:
        raise ValueError("Unsupported match status")
    match = await session.scalar(select(RecallMatch).where(RecallMatch.id == match_id))
    if not match:
        raise LookupError("Match not found")
    action = "reopened" if status == "needs_review" else status
    match.status = status
    match.reviewed_at = datetime.now(timezone.utc)
    await session.refresh(match, attribute_names=["recall", "inventory_item"])
    exposure = calculate_exposure(
        match.recall,
        match.inventory_item,
        float(match.score),
        match.signals,
        status=status,
    )
    match.exposure_score = Decimal(str(exposure["exposure_score"]))
    match.exposure_level = exposure["exposure_level"]
    match.exposure_factors = exposure["exposure_factors"]
    session.add(HumanReview(recall_match_id=match.id, action=action, note=note, reviewer_name=reviewer_name))
    session.add(
        AuditEvent(
            entity_type="recall_match",
            entity_id=match.id,
            event_type=f"match.{action}",
            actor_type="user",
            actor_label=reviewer_name,
            metadata_={"note": note},
        )
    )
    await session.commit()
    await session.refresh(match)
    return match


async def get_match_with_relations(session: AsyncSession, match_id: Any) -> RecallMatch | None:
    return await session.scalar(
        select(RecallMatch)
        .options(selectinload(RecallMatch.inventory_item), selectinload(RecallMatch.recall))
        .where(RecallMatch.id == match_id)
    )
