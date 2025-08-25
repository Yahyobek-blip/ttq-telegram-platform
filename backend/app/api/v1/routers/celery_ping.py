# backend/app/api/v1/routers/celery_ping.py
from fastapi import APIRouter

from app.services.tasks import ping

router = APIRouter(prefix="/celery", tags=["celery"])


@router.get("/ping")
def trigger_ping():
    task = ping.delay()
    return {"task_id": task.id}
