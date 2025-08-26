"""enrich bots: tg_bot_id, org_id, is_active, token meta (idempotent)

Revision ID: 2025_08_26_000003_bots_enrich
Revises: 2025_08_26_000002_accounts
Create Date: 2025-08-26 17:35:00
"""

from __future__ import annotations

from alembic import op

# revision identifiers, used by Alembic.
revision = "2025_08_26_000003_bots_enrich"
down_revision = "2025_08_26_000002_accounts"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # --- колонки: добавляем только если их нет ---
    op.execute("ALTER TABLE bots ADD COLUMN IF NOT EXISTS tg_bot_id BIGINT")
    op.execute("ALTER TABLE bots ADD COLUMN IF NOT EXISTS organization_id UUID")
    op.execute("ALTER TABLE bots ADD COLUMN IF NOT EXISTS is_active BOOLEAN")
    op.execute("ALTER TABLE bots ADD COLUMN IF NOT EXISTS token_hash VARCHAR(64)")
    op.execute("ALTER TABLE bots ADD COLUMN IF NOT EXISTS token_last4 VARCHAR(8)")
    op.execute("ALTER TABLE bots ADD COLUMN IF NOT EXISTS token_rotated_at TIMESTAMPTZ")

    # is_active: выставим DEFAULT TRUE и NOT NULL (без падений)
    op.execute("ALTER TABLE bots ALTER COLUMN is_active SET DEFAULT TRUE")
    op.execute("UPDATE bots SET is_active = TRUE WHERE is_active IS NULL")
    op.execute("ALTER TABLE bots ALTER COLUMN is_active SET NOT NULL")

    # --- уникальность tg_bot_id (разрешаем несколько NULL) ---
    # Создаём частичный уникальный индекс, если его ещё нет.
    op.execute(
        """
        CREATE UNIQUE INDEX IF NOT EXISTS uq_bots_tg_bot_id
        ON bots (tg_bot_id)
        WHERE tg_bot_id IS NOT NULL
        """
    )

    # --- FK на organizations(id) (если ещё нет) ---
    op.execute(
        """
        DO $$
        BEGIN
          IF NOT EXISTS (
            SELECT 1
            FROM information_schema.table_constraints
            WHERE table_name = 'bots'
              AND constraint_type = 'FOREIGN KEY'
              AND constraint_name = 'fk_bots_organization_id_organizations'
          ) THEN
            ALTER TABLE bots
            ADD CONSTRAINT fk_bots_organization_id_organizations
            FOREIGN KEY (organization_id)
            REFERENCES organizations(id)
            ON DELETE SET NULL;
          END IF;
        END$$;
        """
    )


def downgrade() -> None:
    # удаляем FK, если он есть
    op.execute("ALTER TABLE bots DROP CONSTRAINT IF EXISTS fk_bots_organization_id_organizations")
    # удаляем уникальный индекс (если вдруг был создан)
    op.execute("DROP INDEX IF EXISTS uq_bots_tg_bot_id")

    # удаляем колонки, если они есть
    op.execute("ALTER TABLE bots DROP COLUMN IF EXISTS token_rotated_at")
    op.execute("ALTER TABLE bots DROP COLUMN IF EXISTS token_last4")
    op.execute("ALTER TABLE bots DROP COLUMN IF EXISTS token_hash")
    op.execute("ALTER TABLE bots DROP COLUMN IF EXISTS is_active")
    op.execute("ALTER TABLE bots DROP COLUMN IF EXISTS organization_id")
    op.execute("ALTER TABLE bots DROP COLUMN IF EXISTS tg_bot_id")
