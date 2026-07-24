import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Index, Numeric, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class Recall(Base, TimestampMixin):
    __tablename__ = "recalls"
    __table_args__ = (
        UniqueConstraint("source", "source_recall_id", name="uq_recalls_source_source_id"),
        Index("ix_recalls_classification", "classification"),
        Index("ix_recalls_recall_initiation_date", "recall_initiation_date"),
        Index("ix_recalls_normalized_product_name", "normalized_product_name"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(50), default="openfda")
    source_recall_id: Mapped[str] = mapped_column(String(160))
    source_url: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str | None] = mapped_column(String(80))
    classification: Mapped[str | None] = mapped_column(String(80))
    product_description: Mapped[str] = mapped_column(Text)
    brand_name: Mapped[str | None] = mapped_column(Text)
    recalling_firm: Mapped[str | None] = mapped_column(Text)
    reason_for_recall: Mapped[str | None] = mapped_column(Text)
    distribution_pattern: Mapped[str | None] = mapped_column(Text)
    recall_initiation_date: Mapped[date | None] = mapped_column(Date)
    report_date: Mapped[date | None] = mapped_column(Date)
    termination_date: Mapped[date | None] = mapped_column(Date)
    normalized_product_name: Mapped[str | None] = mapped_column(Text)
    normalized_brand_name: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    raw_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    matches: Mapped[list["RecallMatch"]] = relationship(back_populates="recall", cascade="all, delete-orphan")


class UploadedFile(Base, TimestampMixin):
    __tablename__ = "uploaded_files"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_type: Mapped[str] = mapped_column(String(80), default="inventory_csv")
    original_filename: Mapped[str] = mapped_column(Text)
    storage_path: Mapped[str | None] = mapped_column(Text)
    row_count: Mapped[int] = mapped_column(default=0)
    valid_row_count: Mapped[int] = mapped_column(default=0)
    invalid_row_count: Mapped[int] = mapped_column(default=0)
    status: Mapped[str] = mapped_column(String(40), default="uploaded")
    error_summary: Mapped[str | None] = mapped_column(Text)


class InventoryItem(Base, TimestampMixin):
    __tablename__ = "inventory_items"
    __table_args__ = (
        Index("ix_inventory_normalized_product_name", "normalized_product_name"),
        Index("ix_inventory_normalized_brand", "normalized_brand"),
        Index("ix_inventory_upc", "upc"),
        Index("ix_inventory_lot_code", "lot_code"),
        Index("ix_inventory_active", "active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_name: Mapped[str] = mapped_column(Text)
    brand: Mapped[str | None] = mapped_column(Text)
    upc: Mapped[str | None] = mapped_column(String(64))
    lot_code: Mapped[str | None] = mapped_column(String(120))
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    unit: Mapped[str | None] = mapped_column(String(40))
    location: Mapped[str | None] = mapped_column(Text)
    location_type: Mapped[str | None] = mapped_column(String(80))
    location_criticality: Mapped[str | None] = mapped_column(String(40))
    public_serving: Mapped[bool] = mapped_column(default=False)
    region: Mapped[str | None] = mapped_column(String(120))
    supplier: Mapped[str | None] = mapped_column(Text)
    purchase_date: Mapped[date | None] = mapped_column(Date)
    normalized_product_name: Mapped[str | None] = mapped_column(Text)
    normalized_brand: Mapped[str | None] = mapped_column(Text)
    uploaded_file_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("uploaded_files.id", ondelete="SET NULL"))
    active: Mapped[bool] = mapped_column(default=True)
    raw_row: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)

    matches: Mapped[list["RecallMatch"]] = relationship(back_populates="inventory_item", cascade="all, delete-orphan")


class RecallMatch(Base, TimestampMixin):
    __tablename__ = "recall_matches"
    __table_args__ = (
        UniqueConstraint("recall_id", "inventory_item_id", name="uq_recall_inventory_match"),
        Index("ix_recall_matches_confidence", "confidence"),
        Index("ix_recall_matches_status", "status"),
        Index("ix_recall_matches_score", "score"),
        Index("ix_recall_matches_exposure_level", "exposure_level"),
        Index("ix_recall_matches_exposure_score", "exposure_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recall_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recalls.id", ondelete="CASCADE"))
    inventory_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("inventory_items.id", ondelete="CASCADE"))
    score: Mapped[Decimal] = mapped_column(Numeric(5, 4))
    confidence: Mapped[str] = mapped_column(String(20))
    exposure_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=0)
    exposure_level: Mapped[str] = mapped_column(String(20), default="low")
    exposure_factors: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="needs_review")
    signals: Mapped[list[dict[str, Any]]] = mapped_column(JSON, default=list)
    explanation: Mapped[str] = mapped_column(Text)
    matched_fields: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    recall: Mapped[Recall] = relationship(back_populates="matches")
    inventory_item: Mapped[InventoryItem] = relationship(back_populates="matches")
    reviews: Mapped[list["HumanReview"]] = relationship(back_populates="recall_match", cascade="all, delete-orphan")


class HumanReview(Base):
    __tablename__ = "human_reviews"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recall_match_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recall_matches.id", ondelete="CASCADE"))
    action: Mapped[str] = mapped_column(String(40))
    note: Mapped[str | None] = mapped_column(Text)
    reviewer_name: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    recall_match: Mapped[RecallMatch] = relationship(back_populates="reviews")


class AuditEvent(Base):
    __tablename__ = "audit_events"
    __table_args__ = (Index("ix_audit_entity", "entity_type", "entity_id"),)

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type: Mapped[str] = mapped_column(String(80))
    entity_id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True))
    event_type: Mapped[str] = mapped_column(String(120))
    actor_type: Mapped[str] = mapped_column(String(40), default="system")
    actor_label: Mapped[str | None] = mapped_column(Text)
    metadata_: Mapped[dict[str, Any]] = mapped_column("metadata", JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ImportStatus(Base):
    __tablename__ = "import_statuses"

    source: Mapped[str] = mapped_column(String(80), primary_key=True)
    status: Mapped[str] = mapped_column(String(40), default="idle")
    imported: Mapped[int] = mapped_column(default=0)
    updated: Mapped[int] = mapped_column(default=0)
    skipped: Mapped[int] = mapped_column(default=0)
    error: Mapped[str | None] = mapped_column(Text)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ModelRun(Base):
    __tablename__ = "model_runs"

    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_type: Mapped[str] = mapped_column(String(120))
    model_name: Mapped[str | None] = mapped_column(Text)
    model_version: Mapped[str | None] = mapped_column(Text)
    input_ref_type: Mapped[str] = mapped_column(String(80))
    input_ref_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    output_ref_type: Mapped[str | None] = mapped_column(String(80))
    output_ref_id: Mapped[uuid.UUID | None] = mapped_column(Uuid(as_uuid=True))
    parameters: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(40), default="queued")
    error_message: Mapped[str | None] = mapped_column(Text)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
