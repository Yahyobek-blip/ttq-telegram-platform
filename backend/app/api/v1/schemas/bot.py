from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class BotBase(BaseModel):
    organization_id: uuid.UUID | None = None
    username: str = Field(max_length=64)
    tg_bot_id: int | None = None
    is_active: bool = True

    model_config = dict(from_attributes=True)


class BotCreate(BotBase):
    pass


class BotUpdate(BaseModel):
    organization_id: uuid.UUID | None = None
    username: str | None = Field(default=None, max_length=64)
    is_active: bool | None = None

    model_config = dict(from_attributes=True)


class BotRead(BotBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
