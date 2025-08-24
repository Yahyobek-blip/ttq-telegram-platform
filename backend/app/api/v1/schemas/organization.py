from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class OrganizationBase(BaseModel):
    name: str = Field(min_length=1, max_length=200)


class OrganizationCreate(OrganizationBase):
    pass


class OrganizationUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)


class OrganizationRead(OrganizationBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
