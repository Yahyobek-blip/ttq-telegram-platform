from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.schemas.org_user import OrgUserCreate, OrgUserRead
from app.db.models.org_user import OrgUser

router = APIRouter(prefix="/org-users", tags=["org-users"])


@router.get("", response_model=list[OrgUserRead])
def list_org_users(db: Session = Depends(get_db)) -> list[OrgUser]:
    res = db.execute(select(OrgUser).order_by(OrgUser.created_at.desc()))
    return list(res.scalars().all())


@router.post("", response_model=OrgUserRead, status_code=status.HTTP_201_CREATED)
def add_membership(payload: OrgUserCreate, db: Session = Depends(get_db)) -> OrgUser:
    instance = OrgUser(**payload.model_dump())
    db.add(instance)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise
    db.refresh(instance)
    return instance


@router.get("/{membership_id}", response_model=OrgUserRead)
def get_membership(membership_id: uuid.UUID, db: Session = Depends(get_db)) -> OrgUser:
    res = db.execute(select(OrgUser).where(OrgUser.id == membership_id))
    obj = res.scalar_one_or_none()
    if not obj:
        raise HTTPException(status_code=404, detail="Membership not found")
    return obj


@router.delete("/{membership_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_membership(membership_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    res = db.execute(delete(OrgUser).where(OrgUser.id == membership_id))
    if res.rowcount == 0:
        raise HTTPException(status_code=404, detail="Membership not found")
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
