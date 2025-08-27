"""fix organizations timestamps default

Revision ID: 2025_08_27_000004
Revises: 2025_08_26_000003_bots_enrich
Create Date: 2025-08-27 21:15:00
"""

from __future__ import annotations

from alembic import op

revision = "2025_08_27_000004"
down_revision = "2025_08_26_000003_bots_enrich"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE organizations ALTER COLUMN created_at SET DEFAULT now()")
    op.execute("ALTER TABLE organizations ALTER COLUMN updated_at SET DEFAULT now()")
    op.execute("UPDATE organizations SET created_at = now() WHERE created_at IS NULL")
    op.execute("UPDATE organizations SET updated_at = now() WHERE updated_at IS NULL")
    op.execute("ALTER TABLE organizations ALTER COLUMN created_at SET NOT NULL")
    op.execute("ALTER TABLE organizations ALTER COLUMN updated_at SET NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE organizations ALTER COLUMN created_at DROP DEFAULT")
    op.execute("ALTER TABLE organizations ALTER COLUMN updated_at DROP DEFAULT")
