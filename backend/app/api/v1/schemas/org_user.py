from __future__ import annotations

from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class OrgUserCreate(BaseModel):
    organization_id: UUID
    user_id: UUID
    role: Optional[str] = "member"  # значения: owner/admin/member (пока строкой)


class OrgUserUpdate(BaseModel):
    role: Optional[str] = None


class OrgUserRead(BaseModel):
    id: UUID
    organization_id: UUID
    user_id: UUID
    role: str
