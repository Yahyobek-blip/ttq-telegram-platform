# backend/tests/conftest.py
from __future__ import annotations

from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

# Подтягиваем модели, чтобы Base.metadata «знала» таблицы
from app.db.models import bot as _m_bot  # noqa: F401
from app.db.models import org_user as _m_org_user  # noqa: F401
from app.db.models import organization as _m_org  # noqa: F401
from app.db.models import user as _m_user  # noqa: F401
from app.db.models.base import Base
from app.db.session import ENGINE, SessionLocal, get_db
from app.main import app
from app.services.celery_app import celery_app


@pytest.fixture(scope="session", autouse=True)
def _db_schema() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=ENGINE)
    try:
        yield
    finally:
        Base.metadata.drop_all(bind=ENGINE)


@pytest.fixture()
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    finally:
        session.close()


@pytest.fixture(autouse=True)
def _celery_eager():
    prev_eager = celery_app.conf.task_always_eager
    prev_store = celery_app.conf.task_store_eager_result
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_store_eager_result = True
    try:
        yield
    finally:
        celery_app.conf.task_always_eager = prev_eager
        celery_app.conf.task_store_eager_result = prev_store


@pytest.fixture()
def client(db: Session):
    """TestClient с подменой get_db на одну и ту же сессию."""

    def _override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()
