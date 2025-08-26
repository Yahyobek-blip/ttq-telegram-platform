from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel

# --- Базовые схемы пользователей ---


class UserCreate(BaseModel):
    display_name: str
    tg_user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None
    is_active: Optional[bool] = None


class UserRead(BaseModel):
    id: UUID
    tg_user_id: int
    display_name: str
    is_active: bool = True
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = None


# --- Схемы для /users/telegram-sync ---


class TelegramSyncIn(BaseModel):
    tg_user_id: int
    username: Optional[str] = None
    display_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: Optional[str] = None
    is_premium: Optional[bool] = False


class MembershipOut(BaseModel):
    org_id: UUID
    role: str


class TelegramSyncOut(BaseModel):
    created: bool
    user: UserRead
    # делаем membership опциональным, чтобы не падать, если нет ни одной организации
    membership: Optional[MembershipOut] = None
