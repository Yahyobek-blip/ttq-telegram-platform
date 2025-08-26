# mypy: ignore-errors
from __future__ import annotations

from celery.result import AsyncResult
from fastapi import APIRouter

from app.api.v1.schemas.task import TaskStatusOut, TaskSubmitIn, TaskSubmitOut
from app.services.celery_app import celery_app

router = APIRouter(prefix="/api/v1/tasks", tags=["tasks"])


@router.post("/long-demo", response_model=TaskSubmitOut)
def submit_long_demo(payload: TaskSubmitIn) -> TaskSubmitOut:
    res = celery_app.send_task(
        "long_demo",
        kwargs={"text": payload.text, "steps": payload.steps, "delay": payload.delay},
    )
    return TaskSubmitOut(task_id=res.id)


@router.get("/{task_id}/status", response_model=TaskStatusOut)
def task_status(task_id: str) -> TaskStatusOut:
    res = AsyncResult(task_id, app=celery_app)
    state = res.state
    meta = res.info if isinstance(res.info, dict) else {}

    # Прогресс из meta (для PENDING/STARTED/PROGRESS)
    progress_pct = int(meta.get("progress_pct", 0)) if isinstance(meta, dict) else 0
    step = int(meta.get("step", 0)) if isinstance(meta, dict) else 0
    total = int(meta.get("total", 0)) if isinstance(meta, dict) else 0

    result = None
    error = None
    tb = None

    if state == "SUCCESS":
        # SUCCESS: res.info = result (dict)
        result = res.result if isinstance(res.result, dict) else {"value": res.result}
        # Пытаемся достать прогресс из result.progress
        prog = {}
        if isinstance(result, dict):
            prog = result.get("progress") or {}
        if isinstance(prog, dict):
            progress_pct = int(prog.get("progress_pct", progress_pct or 100))
            step = int(prog.get("step", step))
            total = int(prog.get("total", total))
        # Если ничего не нашлось — показываем 100% по умолчанию
        if not progress_pct:
            progress_pct = 100

    elif state == "FAILURE":
        error = str(res.info)
        tb = res.traceback

    return TaskStatusOut(
        id=task_id,
        state=state,
        progress_pct=progress_pct,
        step=step,
        total=total,
        result=result,
        error=error,
        traceback=tb,
    )
