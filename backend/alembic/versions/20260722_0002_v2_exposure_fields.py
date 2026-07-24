"""v2 exposure fields

Revision ID: 20260722_0002
Revises: 20260722_0001
Create Date: 2026-07-22
"""

from alembic import op
import sqlalchemy as sa

revision = "20260722_0002"
down_revision = "20260722_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("inventory_items", sa.Column("location_type", sa.String(length=80), nullable=True))
    op.add_column("inventory_items", sa.Column("location_criticality", sa.String(length=40), nullable=True))
    op.add_column("inventory_items", sa.Column("public_serving", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("inventory_items", sa.Column("region", sa.String(length=120), nullable=True))
    op.add_column("recall_matches", sa.Column("exposure_score", sa.Numeric(5, 2), nullable=False, server_default="0"))
    op.add_column("recall_matches", sa.Column("exposure_level", sa.String(length=20), nullable=False, server_default="low"))
    op.add_column("recall_matches", sa.Column("exposure_factors", sa.JSON(), nullable=False, server_default="{}"))
    op.create_index("ix_recall_matches_exposure_level", "recall_matches", ["exposure_level"])
    op.create_index("ix_recall_matches_exposure_score", "recall_matches", ["exposure_score"])


def downgrade() -> None:
    op.drop_index("ix_recall_matches_exposure_score", table_name="recall_matches")
    op.drop_index("ix_recall_matches_exposure_level", table_name="recall_matches")
    op.drop_column("recall_matches", "exposure_factors")
    op.drop_column("recall_matches", "exposure_level")
    op.drop_column("recall_matches", "exposure_score")
    op.drop_column("inventory_items", "region")
    op.drop_column("inventory_items", "public_serving")
    op.drop_column("inventory_items", "location_criticality")
    op.drop_column("inventory_items", "location_type")
