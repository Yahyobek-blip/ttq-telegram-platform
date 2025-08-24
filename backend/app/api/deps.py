from __future__ import annotations

from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import _build_sync_url  # у тебя уже есть

_engine = create_engine(_build_sync_url(), future=True)
_SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False, future=True)


def get_db() -> Iterator[Session]:
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()
