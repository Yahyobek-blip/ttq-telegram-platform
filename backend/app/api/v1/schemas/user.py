from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    display_name: str = Field(max_length=128)
    tg_user_id: int | None = None
    is_active: bool = True

    model_config = dict(from_attributes=True)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    display_name: str | None = Field(default=None, max_length=128)
    is_active: bool | None = None

    model_config = dict(from_attributes=True)


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
