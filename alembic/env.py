from __future__ import annotations

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# чтобы 'app' корректно импортировался из /app
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from app.db import models as _models  # noqa: F401,E402
from app.db.models.base import Base  # noqa: E402

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url() -> str:
    user = os.getenv("POSTGRES_USER", "ttq")
    password = os.getenv("POSTGRES_PASSWORD", "ttq")
    host = os.getenv("POSTGRES_HOST", "postgres")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "ttq_dev")
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode' without reading ini section."""
    connectable = create_engine(get_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
