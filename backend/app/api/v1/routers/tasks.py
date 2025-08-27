# mypy: ignore-errors
from __future__ import annotations

from typing import Any, Dict

from celery import states
from celery.result import AsyncResult
from fastapi import APIRouter, HTTPException, status

from app.api.v1.schemas.task import (
    TaskEnqueueIn,
    TaskRevokeIn,
    TaskRevokeOut,
    TaskStatusOut,
    TaskSubmitIn,
    TaskSubmitOut,
)
from app.services.celery_app import celery_app
from app.services.tasks import long_demo, ping

# Этот роутер подключается без общего префикса в main.py — держим префикс здесь
router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])

# Разрешённые задачи -> реальные Celery task-объекты
ALLOWED_TASKS: Dict[str, Any] = {
    "long_demo": long_demo,
    "ping": ping,
}


@router.get("/allowed")
def list_allowed_tasks() -> list[str]:
    return sorted(ALLOWED_TASKS.keys())


@router.post("/enqueue", response_model=TaskSubmitOut)
def enqueue_task(payload: TaskEnqueueIn) -> TaskSubmitOut:
    task = ALLOWED_TASKS.get(payload.task_name)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not Found")
    # apply_async уважает eager и backend — без ворнингов
    async_res = task.apply_async(kwargs=payload.kwargs or {})
    return TaskSubmitOut(task_id=async_res.id)


@router.post("/long-demo", response_model=TaskSubmitOut)
def submit_long_demo(payload: TaskSubmitIn) -> TaskSubmitOut:
    async_res = long_demo.apply_async(
        kwargs={"text": payload.text, "steps": payload.steps, "delay": payload.delay}
    )
    return TaskSubmitOut(task_id=async_res.id)


@router.get("/{task_id}/status", response_model=TaskStatusOut)
def task_status(task_id: str) -> TaskStatusOut:
    res = AsyncResult(task_id, app=celery_app)
    state = res.state
    info = res.info if isinstance(res.info, dict) else {}
    progress = info.get("progress", {}) if isinstance(info, dict) else {}

    error = None
    tb = None
    result: Any | None = None

    if state == states.FAILURE:
        error = str(res.info)
        tb = res.traceback
    elif state == states.SUCCESS:
        result = res.result if isinstance(res.result, dict) else {"value": res.result}

    return TaskStatusOut(
        id=task_id,
        state=state,
        progress_pct=int(progress.get("progress_pct", 0) or 0),
        step=int(progress.get("step", 0) or 0),
        total=int(progress.get("total", 0) or 0),
        result=result,
        error=error,
        traceback=tb,
    )


# Удобный алиас: /result возвращает то же, что /status
@router.get("/{task_id}/result", response_model=TaskStatusOut)
def task_result(task_id: str) -> TaskStatusOut:
    return task_status(task_id)


@router.post("/revoke", response_model=TaskRevokeOut)
def revoke_task(payload: TaskRevokeIn) -> TaskRevokeOut:
    celery_app.control.revoke(payload.task_id, terminate=payload.terminate)
    # Попробуем понять состояние
    res = AsyncResult(payload.task_id, app=celery_app)
    revoked = res.state == states.REVOKED
    return TaskRevokeOut(task_id=payload.task_id, revoked=revoked)
