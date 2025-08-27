from __future__ import annotations

from typing import cast
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.v1.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.db.models.organization import Organization
from app.db.session import get_db

router = APIRouter(prefix="/api/v1/organizations", tags=["organizations"])


def _to_read(org: Organization) -> OrganizationRead:
    # pydantic v2 typing может выглядеть как Any для mypy — подскажем явно
    return cast(OrganizationRead, OrganizationRead.model_validate(org, from_attributes=True))


@router.get("", response_model=list[OrganizationRead])
def list_organizations(
    q: str | None = Query(default=None, description="substring filter"),
    db: Session = Depends(get_db),
) -> list[OrganizationRead]:
    stmt = select(Organization)
    if q:
        stmt = stmt.where(func.lower(Organization.name).like(f"%{q.lower()}%"))
    if hasattr(Organization, "created_at"):
        stmt = stmt.order_by(Organization.created_at.asc())
    rows = db.execute(stmt).scalars().all()
    return [_to_read(r) for r in rows]


@router.get("/{org_id}", response_model=OrganizationRead)
def get_organization(org_id: UUID, db: Session = Depends(get_db)) -> OrganizationRead:
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return _to_read(org)


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(
    payload: OrganizationCreate, db: Session = Depends(get_db)
) -> OrganizationRead:
    exists = (
        db.execute(
            select(Organization).where(func.lower(Organization.name) == payload.name.lower())
        )
        .scalars()
        .first()
    )
    if exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="name already exists")

    org = Organization(name=payload.name)
    db.add(org)
    db.commit()
    db.refresh(org)
    return _to_read(org)


@router.patch("/{org_id}", response_model=OrganizationRead)
def patch_organization(
    org_id: UUID, payload: OrganizationUpdate, db: Session = Depends(get_db)
) -> OrganizationRead:
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if payload.name and payload.name != org.name:
        clash = (
            db.execute(
                select(Organization).where(
                    func.lower(Organization.name) == payload.name.lower(),
                    Organization.id != org.id,
                )
            )
            .scalars()
            .first()
        )
        if clash:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="name already exists")
        org.name = payload.name

    db.add(org)
    db.commit()
    db.refresh(org)
    return _to_read(org)


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_organization(org_id: UUID, db: Session = Depends(get_db)) -> None:
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    db.delete(org)
    db.commit()
