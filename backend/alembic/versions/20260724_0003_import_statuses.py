"""import statuses

Revision ID: 20260724_0003
Revises: 20260722_0002
Create Date: 2026-07-24
"""

from alembic import op
import sqlalchemy as sa

revision = "20260724_0003"
down_revision = "20260722_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "import_statuses",
        sa.Column("source", sa.String(length=80), primary_key=True),
        sa.Column("status", sa.String(length=40), nullable=False, server_default="idle"),
        sa.Column("imported", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("skipped", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("import_statuses")
