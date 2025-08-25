from __future__ import annotations

from uuid import UUID, uuid4

from fastapi import (  # ← добавили Response
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Response,
    status,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.schemas.organization import OrganizationCreate, OrganizationRead, OrganizationUpdate
from app.db.models.organization import Organization

router = APIRouter(prefix="/organizations", tags=["organizations"])


@router.get("", response_model=list[OrganizationRead])
def list_organizations(
    db: Session = Depends(get_db),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    items = db.execute(select(Organization).offset(offset).limit(limit)).scalars().all()
    return items


@router.post("", response_model=OrganizationRead, status_code=status.HTTP_201_CREATED)
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db)):
    org = Organization(id=uuid4(), name=payload.name)
    db.add(org)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="name already exists")
    db.refresh(org)
    return org


@router.get("/{org_id}", response_model=OrganizationRead)
def get_organization(org_id: UUID, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
    return org


@router.patch("/{org_id}", response_model=OrganizationRead)
def update_organization(org_id: UUID, payload: OrganizationUpdate, db: Session = Depends(get_db)):
    org = db.get(Organization, org_id)
    if not org:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")

    if payload.name is not None:
        org.name = payload.name

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="name already exists")
    db.refresh(org)
    return org


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,  # ← ключевая строка
)
def delete_organization(org_id: UUID, db: Session = Depends(get_db)) -> Response:
    # Вариант 1: через ORM
    org = db.get(Organization, org_id)
    if org:
        db.delete(org)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
    # Вариант 2 (эквивалентно): db.execute(delete(Organization).where(Organization.id == org_id)); db.commit(); return Response(status_code=204)
