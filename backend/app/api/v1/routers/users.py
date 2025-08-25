from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.api.v1.schemas.user import UserCreate, UserRead, UserUpdate
from app.db.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserRead])
def list_users(db: Session = Depends(get_db)):
    res = db.execute(select(User).order_by(User.created_at.desc()))
    return res.scalars().all()


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    u = User(id=uuid.uuid4(), display_name=payload.display_name, tg_user_id=payload.tg_user_id)
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: uuid.UUID, payload: UserUpdate, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    if payload.display_name is not None:
        u.display_name = payload.display_name
    if payload.tg_user_id is not None:
        u.tg_user_id = payload.tg_user_id
    db.commit()
    db.refresh(u)
    return u


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)) -> Response:
    res = db.execute(delete(User).where(User.id == user_id))
    if res.rowcount:
        db.commit()
    return Response(status_code=204)
