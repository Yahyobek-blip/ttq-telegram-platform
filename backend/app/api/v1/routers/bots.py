from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.api.v1.schemas.bot import BotCreate, BotRead, BotUpdate
from app.db.models.bot import Bot

router = APIRouter(prefix="/bots", tags=["bots"])


@router.get("", response_model=list[BotRead])
async def list_bots(
    db: Annotated[AsyncSession, Depends(get_db)],
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
) -> list[Bot]:
    res = await db.execute(select(Bot).order_by(Bot.created_at.desc()).offset(offset).limit(limit))
    return list(res.scalars().all())


@router.post("", response_model=BotRead, status_code=status.HTTP_201_CREATED)
async def create_bot(payload: BotCreate, db: Annotated[AsyncSession, Depends(get_db)]) -> Bot:
    obj = Bot(id=uuid.uuid4(), username=payload.username)
    db.add(obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")
    await db.refresh(obj)
    return obj


@router.get("/{bot_id}", response_model=BotRead)
async def get_bot(bot_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> Bot:
    obj = await db.get(Bot, bot_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return obj


@router.patch("/{bot_id}", response_model=BotRead)
async def update_bot(
    bot_id: uuid.UUID, payload: BotUpdate, db: Annotated[AsyncSession, Depends(get_db)]
) -> Bot:
    obj = await db.get(Bot, bot_id)
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if payload.username is not None:
        obj.username = payload.username

    active = payload.is_active
    if active is not None:
        obj.is_active = active

    if payload.organization_id is not None:
        obj.organization_id = payload.organization_id

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="username already exists")
    await db.refresh(obj)
    return obj


@router.delete("/{bot_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_bot(bot_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)]) -> Response:
    obj = await db.get(Bot, bot_id)
    if obj:
        await db.delete(obj)
        await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
