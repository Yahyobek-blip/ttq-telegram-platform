from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class OrgUserBase(BaseModel):
    organization_id: uuid.UUID
    user_id: uuid.UUID
    role: str = Field(pattern="^(owner|admin|member)$")

    model_config = dict(from_attributes=True)


class OrgUserCreate(OrgUserBase):
    pass


class OrgUserRead(OrgUserBase):
    id: uuid.UUID
    created_at: datetime
