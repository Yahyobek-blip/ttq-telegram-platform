from __future__ import annotations

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings  # у тебя уже есть settings


def _build_sync_url() -> str:
    user = os.getenv("POSTGRES_USER", settings.postgres_user)
    password = os.getenv("POSTGRES_PASSWORD", settings.postgres_password)
    host = os.getenv("POSTGRES_HOST", settings.postgres_host)
    port = os.getenv("POSTGRES_PORT", str(settings.postgres_port))
    db = os.getenv("POSTGRES_DB", settings.postgres_db)
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db}"


ENGINE = create_engine(_build_sync_url(), pool_pre_ping=True, echo=False, future=True)
SessionLocal = sessionmaker(bind=ENGINE, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
