"""accounts: users, bots, org_users

Revision ID: 2025_08_26_000002_accounts
Revises: 2025_08_24_000001_init
Create Date: 2025-08-26 00:00:02
"""

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from alembic import op

# revision identifiers, used by Alembic.
revision = "2025_08_26_000002_accounts"
down_revision = "2025_08_24_000001_init"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto";')

    # Создать enum, если его ещё нет (иначе пропустить)
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'org_role') THEN
                CREATE TYPE org_role AS ENUM ('owner', 'admin', 'member');
            END IF;
        END
        $$;
        """
    )

    # users
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column("tg_user_id", sa.BigInteger(), nullable=True, unique=True),
        sa.Column("display_name", sa.String(length=128), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # bots
    op.create_table(
        "bots",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "organization_id",
            sa.UUID(),
            sa.ForeignKey("organizations.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("tg_bot_id", sa.BigInteger(), nullable=True, unique=True),
        sa.Column("username", sa.String(length=64), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    # org_users — используем уже существующий тип, НЕ создаём заново
    role_enum = PGEnum("owner", "admin", "member", name="org_role", create_type=False)

    op.create_table(
        "org_users",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), primary_key=True),
        sa.Column(
            "organization_id",
            sa.UUID(),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.UUID(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False
        ),
        sa.Column("role", role_enum, nullable=False, server_default=sa.text("'member'")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_org_user"),
    )


def downgrade() -> None:
    op.drop_table("org_users")
    op.drop_table("bots")
    op.drop_table("users")
    # тип можно оставить; если он больше не нужен:
    # op.execute("DROP TYPE IF EXISTS org_role;")
