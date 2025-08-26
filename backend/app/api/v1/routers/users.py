# mypy: ignore-errors
# backend/app/api/v1/routers/users.py
from __future__ import annotations

from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

# --- DB session dependency ---
try:
    # если уже есть готовый get_db – используем его
    from app.db.session import get_db  # type: ignore
except Exception:
    # fallback на SessionLocal, если get_db отсутствует
    from app.db.session import SessionLocal  # type: ignore

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


from app.db.models.org_user import OrgUser  # type: ignore
from app.db.models.organization import Organization  # type: ignore

# --- ORM модели ---
from app.db.models.user import User  # type: ignore

# enum роли может отсутствовать — сделаем мягкий импорт
try:
    from app.db.models.org_user import OrgRole  # type: ignore
except Exception:

    class OrgRole:  # simple fallback
        owner = "owner"
        admin = "admin"
        member = "member"


router = APIRouter(prefix="/api/v1/users", tags=["users"])


# --------- Вспомогательное ---------
def user_to_dict(u: User) -> Dict[str, Any]:
    """Безопасная сериализация: добавляем только реально существующие атрибуты."""
    data: Dict[str, Any] = {
        "id": getattr(u, "id", None),
        "tg_user_id": getattr(u, "tg_user_id", None),
        "display_name": getattr(u, "display_name", None),
        "is_active": getattr(u, "is_active", None),
    }
    # опциональные поля — добавляем только если есть в модели
    for opt in ("username", "first_name", "last_name", "language_code", "is_premium"):
        if hasattr(u, opt):
            data[opt] = getattr(u, opt)
    return data


def first_any_organization(db: Session) -> Optional[Organization]:
    """Возвращаем первую попавшуюся организацию (по created_at, если поле есть)."""
    try:
        # если у модели есть created_at – отсортируем по нему
        if hasattr(Organization, "created_at"):
            stmt = select(Organization).order_by(Organization.created_at.asc())
        else:
            stmt = select(Organization)
        return db.execute(stmt).scalar_one_or_none()
    except Exception:
        # на всякий случай – вообще без сортировок
        return db.execute(select(Organization)).scalar_one_or_none()


# --------- Эндпоинты ---------
@router.get("", response_model=List[Dict[str, Any]])
def list_users(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(
        default=None, description="Поиск по подстроке (display_name/username, если есть)"
    ),
    tg_user_id: Optional[int] = Query(default=None, description="Точный поиск по Telegram user id"),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    stmt = select(User)

    # фильтрация по tg_user_id имеет приоритет
    if tg_user_id is not None:
        stmt = stmt.where(User.tg_user_id == tg_user_id)
    elif q:
        filters = []
        # display_name почти наверняка есть
        if hasattr(User, "display_name"):
            filters.append(User.display_name.ilike(f"%{q}%"))
        # username может не существовать — добавим, только если есть
        if hasattr(User, "username"):
            filters.append(getattr(User, "username").ilike(f"%{q}%"))
        if filters:
            stmt = stmt.where(or_(*filters))

    # сортировка
    if hasattr(User, "display_name"):
        stmt = stmt.order_by(User.display_name.asc())
    elif hasattr(User, "tg_user_id"):
        stmt = stmt.order_by(User.tg_user_id.asc())

    stmt = stmt.offset(offset).limit(limit)
    users = db.execute(stmt).scalars().all()
    return [user_to_dict(u) for u in users]


@router.post("/telegram-sync", response_model=Dict[str, Any], status_code=status.HTTP_200_OK)
def telegram_sync(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
):
    """
    Синхронизируем пользователя по tg_user_id.
    Тело запроса может содержать:
      - tg_user_id (int, обязателен)
      - display_name (str, опционально)
      - username / first_name / last_name / language_code / is_premium (опц., будут применены только если такие поля есть в модели)
    """
    tg_user_id = payload.get("tg_user_id")
    if tg_user_id is None:
        raise HTTPException(status_code=422, detail="tg_user_id is required")

    u = db.execute(select(User).where(User.tg_user_id == tg_user_id)).scalar_one_or_none()
    created = False

    if u is None:
        # создаём пользователя с минимальным набором
        u = User(
            tg_user_id=tg_user_id,
            display_name=payload.get("display_name") or f"user_{tg_user_id}",
            is_active=True,
        )
        # мягко проставим дополнительные поля, если они реально есть в модели
        for field in ("username", "first_name", "last_name", "language_code", "is_premium"):
            if field in payload and hasattr(u, field):
                setattr(u, field, payload[field])

        db.add(u)
        db.flush()  # чтобы получить u.id
        created = True
    else:
        # апдейтим только существующие в модели поля и только если они переданы
        dirty = False
        for field in (
            "display_name",
            "language_code",
            "is_premium",
            "first_name",
            "last_name",
            "username",
        ):
            if field in payload and hasattr(u, field):
                val = payload[field]
                if getattr(u, field) != val:
                    setattr(u, field, val)
                    dirty = True
        if dirty:
            db.flush()

    # пробуем привязать к "дефолтной" (первой попавшейся) организации
    membership_info: Optional[Dict[str, Any]] = None
    org = first_any_organization(db)
    if org is not None:
        # существует ли связь
        exists = db.execute(
            select(OrgUser).where(OrgUser.organization_id == org.id, OrgUser.user_id == u.id)
        ).scalar_one_or_none()

        if exists is None:
            # роль как строка по умолчанию
            default_role = getattr(OrgRole, "member", "member")
            ou = OrgUser(organization_id=org.id, user_id=u.id, role=default_role)
            db.add(ou)
            db.flush()
            membership_info = {"org_id": org.id, "role": default_role}
        else:
            membership_info = {
                "org_id": exists.organization_id,
                "role": getattr(exists, "role", "member"),
            }

    db.commit()

    return {
        "created": created,
        "user": user_to_dict(u),
        "membership": membership_info,
    }
