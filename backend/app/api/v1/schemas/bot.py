from __future__ import annotations

from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from pydantic import BaseModel, Field, StringConstraints

# Тип для username с проверками
Username = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=64),
]


# ----- INPUT / MUTATION -----


class BotCreate(BaseModel):
    """Создание бота в нашей системе (НЕ BotFather)."""

    username: Username = Field(..., description="Юзернейм бота без @")


class BotUpdate(BaseModel):
    """Частичное обновление."""

    tg_bot_id: Optional[int] = Field(None, description="numeric id бота в Telegram")
    organization_id: Optional[UUID] = Field(None, description="привязка к организации")
    is_active: Optional[bool] = Field(None, description="вкл/выкл")


class BotRotateTokenIn(BaseModel):
    """Временная передача полного токена для ротации (мы его не храним)."""

    token: str = Field(
        ..., min_length=10, description="Полный токен TG-бота (например 123456:ABC...)"
    )


# ----- OUTPUT / READ -----


class BotRead(BaseModel):
    id: UUID
    username: str
    tg_bot_id: Optional[int] = None
    organization_id: Optional[UUID] = None
    is_active: bool = True
    token_last4: Optional[str] = None
    token_rotated_at: Optional[datetime] = None


class BotRotateTokenOut(BaseModel):
    id: UUID
    token_last4: str
    token_rotated_at: datetime
