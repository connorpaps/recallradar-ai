"""initial schema

Revision ID: 20260722_0001
Revises:
Create Date: 2026-07-22
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260722_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recalls",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_recall_id", sa.String(length=160), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=80), nullable=True),
        sa.Column("classification", sa.String(length=80), nullable=True),
        sa.Column("product_description", sa.Text(), nullable=False),
        sa.Column("brand_name", sa.Text(), nullable=True),
        sa.Column("recalling_firm", sa.Text(), nullable=True),
        sa.Column("reason_for_recall", sa.Text(), nullable=True),
        sa.Column("distribution_pattern", sa.Text(), nullable=True),
        sa.Column("recall_initiation_date", sa.Date(), nullable=True),
        sa.Column("report_date", sa.Date(), nullable=True),
        sa.Column("termination_date", sa.Date(), nullable=True),
        sa.Column("normalized_product_name", sa.Text(), nullable=True),
        sa.Column("normalized_brand_name", sa.Text(), nullable=True),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("raw_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.UniqueConstraint("source", "source_recall_id", name="uq_recalls_source_source_id"),
    )
    op.create_index("ix_recalls_classification", "recalls", ["classification"])
    op.create_index("ix_recalls_recall_initiation_date", "recalls", ["recall_initiation_date"])
    op.create_index("ix_recalls_normalized_product_name", "recalls", ["normalized_product_name"])

    op.create_table(
        "uploaded_files",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("file_type", sa.String(length=80), nullable=False),
        sa.Column("original_filename", sa.Text(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=False),
        sa.Column("valid_row_count", sa.Integer(), nullable=False),
        sa.Column("invalid_row_count", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    op.create_table(
        "inventory_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("product_name", sa.Text(), nullable=False),
        sa.Column("brand", sa.Text(), nullable=True),
        sa.Column("upc", sa.String(length=64), nullable=True),
        sa.Column("lot_code", sa.String(length=120), nullable=True),
        sa.Column("quantity", sa.Numeric(12, 2), nullable=True),
        sa.Column("unit", sa.String(length=40), nullable=True),
        sa.Column("location", sa.Text(), nullable=True),
        sa.Column("supplier", sa.Text(), nullable=True),
        sa.Column("purchase_date", sa.Date(), nullable=True),
        sa.Column("normalized_product_name", sa.Text(), nullable=True),
        sa.Column("normalized_brand", sa.Text(), nullable=True),
        sa.Column("uploaded_file_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("raw_row", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_file_id"], ["uploaded_files.id"], ondelete="SET NULL"),
    )
    op.create_index("ix_inventory_normalized_product_name", "inventory_items", ["normalized_product_name"])
    op.create_index("ix_inventory_normalized_brand", "inventory_items", ["normalized_brand"])
    op.create_index("ix_inventory_upc", "inventory_items", ["upc"])
    op.create_index("ix_inventory_lot_code", "inventory_items", ["lot_code"])
    op.create_index("ix_inventory_active", "inventory_items", ["active"])

    op.create_table(
        "recall_matches",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recall_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("inventory_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score", sa.Numeric(5, 4), nullable=False),
        sa.Column("confidence", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("signals", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("matched_fields", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["recall_id"], ["recalls.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["inventory_item_id"], ["inventory_items.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("recall_id", "inventory_item_id", name="uq_recall_inventory_match"),
    )
    op.create_index("ix_recall_matches_confidence", "recall_matches", ["confidence"])
    op.create_index("ix_recall_matches_status", "recall_matches", ["status"])
    op.create_index("ix_recall_matches_score", "recall_matches", ["score"])

    op.create_table(
        "human_reviews",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("recall_match_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=40), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("reviewer_name", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["recall_match_id"], ["recall_matches.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("entity_type", sa.String(length=80), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=120), nullable=False),
        sa.Column("actor_type", sa.String(length=40), nullable=False),
        sa.Column("actor_label", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("ix_audit_entity", "audit_events", ["entity_type", "entity_id"])

    op.create_table(
        "model_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("run_type", sa.String(length=120), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=True),
        sa.Column("model_version", sa.Text(), nullable=True),
        sa.Column("input_ref_type", sa.String(length=80), nullable=False),
        sa.Column("input_ref_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("output_ref_type", sa.String(length=80), nullable=True),
        sa.Column("output_ref_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("parameters", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("metrics", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("model_runs")
    op.drop_index("ix_audit_entity", table_name="audit_events")
    op.drop_table("audit_events")
    op.drop_table("human_reviews")
    op.drop_index("ix_recall_matches_score", table_name="recall_matches")
    op.drop_index("ix_recall_matches_status", table_name="recall_matches")
    op.drop_index("ix_recall_matches_confidence", table_name="recall_matches")
    op.drop_table("recall_matches")
    op.drop_index("ix_inventory_active", table_name="inventory_items")
    op.drop_index("ix_inventory_lot_code", table_name="inventory_items")
    op.drop_index("ix_inventory_upc", table_name="inventory_items")
    op.drop_index("ix_inventory_normalized_brand", table_name="inventory_items")
    op.drop_index("ix_inventory_normalized_product_name", table_name="inventory_items")
    op.drop_table("inventory_items")
    op.drop_table("uploaded_files")
    op.drop_index("ix_recalls_normalized_product_name", table_name="recalls")
    op.drop_index("ix_recalls_recall_initiation_date", table_name="recalls")
    op.drop_index("ix_recalls_classification", table_name="recalls")
    op.drop_table("recalls")
