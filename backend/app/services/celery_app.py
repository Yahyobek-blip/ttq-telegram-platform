import os

from celery import Celery

celery_app = Celery(
    "ttq_app",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/0"),
)

# Автопоиск задач в пакете app.services
celery_app.autodiscover_tasks(packages=["app.services"])
