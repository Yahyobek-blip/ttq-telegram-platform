from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

try:
    from pydantic import ConfigDict  # pydantic v2

    _V2 = True
except Exception:  # pragma: no cover
    _V2 = False


# Узкая демо-модель для /long-demo
class TaskSubmitIn(BaseModel):
    text: str = Field("", description="Произвольный текст")
    steps: int = Field(5, ge=1, le=100, description="Количество шагов")
    delay: float = Field(0.5, ge=0, le=10, description="Задержка между шагами (сек)")


# Универсальный инпут для /enqueue
class TaskEnqueueIn(BaseModel):
    task_name: str = Field(..., description="Имя разрешённой Celery-задачи")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Аргументы задачи")


class TaskSubmitOut(BaseModel):
    task_id: str


class TaskStatusOut(BaseModel):
    id: str
    state: str  # PENDING | STARTED | PROGRESS | SUCCESS | FAILURE | RETRY | REVOKED
    progress_pct: int = 0
    step: int = 0
    total: int = 0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    traceback: Optional[str] = None

    if _V2:
        model_config = ConfigDict(from_attributes=True)


class TaskRevokeIn(BaseModel):
    task_id: str
    terminate: bool = False


class TaskRevokeOut(BaseModel):
    task_id: str
    revoked: bool
