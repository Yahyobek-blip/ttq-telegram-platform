# mypy: ignore-errors
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.schemas.bot import (
    BotCreate,
    BotRead,
    BotRotateTokenIn,
    BotRotateTokenOut,
    BotUpdate,
)
from app.db.models.bot import Bot

router = APIRouter(prefix="/api/v1/bots", tags=["bots"])


def to_read_model(b: Bot) -> BotRead:
    return BotRead.model_validate(b, from_attributes=True)


@router.get("", response_model=List[BotRead])
def list_bots(
    q: Optional[str] = Query(None, description="Поиск по username (подстрока)"),
    org_id: Optional[UUID] = Query(None, description="Фильтр по организации"),
    is_active: Optional[bool] = Query(None, description="Фильтр по активности"),
    limit: int = Query(50, ge=1, le=200, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: Session = Depends(get_db),
) -> List[BotRead]:
    stmt = select(Bot)
    if q:
        stmt = stmt.where(Bot.username.ilike(f"%{q}%"))  # type: ignore[attr-defined]
    if org_id is not None:
        stmt = stmt.where(Bot.organization_id == org_id)
    if is_active is not None:
        stmt = stmt.where(Bot.is_active == is_active)

    bots = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    return [to_read_model(b) for b in bots]


@router.post("", response_model=BotRead, status_code=status.HTTP_201_CREATED)
def create_bot(payload: BotCreate, db: Session = Depends(get_db)) -> BotRead:
    exists = db.execute(select(Bot).where(Bot.username == payload.username)).scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Bot with this username already exists"
        )

    bot = Bot(username=payload.username)
    db.add(bot)
    db.commit()
    db.refresh(bot)
    return to_read_model(bot)


@router.get("/{bot_id}", response_model=BotRead)
def get_bot(bot_id: UUID, db: Session = Depends(get_db)) -> BotRead:
    bot = db.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")
    return to_read_model(bot)


@router.patch("/{bot_id}", response_model=BotRead)
def update_bot(bot_id: UUID, payload: BotUpdate, db: Session = Depends(get_db)) -> BotRead:
    bot = db.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    if payload.tg_bot_id is not None:
        bot.tg_bot_id = payload.tg_bot_id
    if payload.organization_id is not None:
        bot.organization_id = payload.organization_id
    if payload.is_active is not None:
        bot.is_active = payload.is_active

    db.commit()
    db.refresh(bot)
    return to_read_model(bot)


@router.post("/{bot_id}/rotate-token", response_model=BotRotateTokenOut)
def rotate_token(
    bot_id: UUID, payload: BotRotateTokenIn, db: Session = Depends(get_db)
) -> BotRotateTokenOut:
    bot = db.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    last4 = payload.token[-4:] if payload.token else None
    bot.token_last4 = last4
    bot.token_rotated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(bot)

    return BotRotateTokenOut(id=bot.id, token_last4=bot.token_last4 or "", token_rotated_at=bot.token_rotated_at)  # type: ignore[arg-type]


@router.delete(
    "/{bot_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
)
def delete_bot(bot_id: UUID, db: Session = Depends(get_db)) -> Response:
    bot = db.get(Bot, bot_id)
    if not bot:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Bot not found")

    db.delete(bot)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
