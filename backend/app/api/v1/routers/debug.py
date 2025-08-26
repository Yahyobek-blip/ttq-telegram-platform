from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.api.deps import get_db

router = APIRouter(prefix="/api/v1", tags=["debug"])


@router.get("/ping")
def ping():
    return {"ok": True, "svc": "backend"}


@router.get("/db-check")
def db_check(db: Session = Depends(get_db)):
    # простейшая проверка коннекта
    v = db.execute(text("SELECT 1")).scalar_one()
    return {"ok": v == 1}
