# mypy: ignore-errors
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.schemas.org_user import OrgUserCreate, OrgUserRead, OrgUserUpdate
from app.db.models.org_user import OrgUser  # Без OrgRole!

router = APIRouter(prefix="/api/v1/org-users", tags=["org-users"])


def to_read_model(m: OrgUser) -> OrgUserRead:
    return OrgUserRead.model_validate(m, from_attributes=True)


@router.get("", response_model=List[OrgUserRead])
def list_memberships(
    org_id: Optional[UUID] = Query(None, description="Фильтр по организации"),
    user_id: Optional[UUID] = Query(None, description="Фильтр по пользователю"),
    role: Optional[str] = Query(None, description="Фильтр по роли (owner/admin/member)"),
    limit: int = Query(50, ge=1, le=200, description="Размер страницы"),
    offset: int = Query(0, ge=0, description="Смещение"),
    db: Session = Depends(get_db),
) -> List[OrgUserRead]:
    stmt = select(OrgUser)
    if org_id is not None:
        stmt = stmt.where(OrgUser.organization_id == org_id)
    if user_id is not None:
        stmt = stmt.where(OrgUser.user_id == user_id)
    if role is not None:
        stmt = stmt.where(OrgUser.role == role)

    rows = db.execute(stmt.offset(offset).limit(limit)).scalars().all()
    return [to_read_model(m) for m in rows]


@router.post("", response_model=OrgUserRead, status_code=status.HTTP_201_CREATED)
def create_membership(payload: OrgUserCreate, db: Session = Depends(get_db)) -> OrgUserRead:
    # уникальность по (organization_id, user_id)
    exists = db.execute(
        select(OrgUser).where(
            OrgUser.organization_id == payload.organization_id,
            OrgUser.user_id == payload.user_id,
        )
    ).scalar_one_or_none()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Membership already exists"
        )

    m = OrgUser(
        organization_id=payload.organization_id,
        user_id=payload.user_id,
        role=payload.role or "member",
    )
    db.add(m)
    db.commit()
    db.refresh(m)
    return to_read_model(m)


@router.patch("/{membership_id}", response_model=OrgUserRead)
def update_membership(
    membership_id: UUID,
    payload: OrgUserUpdate,
    db: Session = Depends(get_db),
) -> OrgUserRead:
    m = db.get(OrgUser, membership_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    if payload.role is not None:
        m.role = payload.role

    db.commit()
    db.refresh(m)
    return to_read_model(m)


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_membership(membership_id: UUID, db: Session = Depends(get_db)) -> Response:
    m = db.get(OrgUser, membership_id)
    if not m:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Membership not found")

    db.delete(m)
    db.commit()
    # 204 без тела
    return Response(status_code=status.HTTP_204_NO_CONTENT)
