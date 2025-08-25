import logging

from app.services.celery_app import celery_app

logger = logging.getLogger(__name__)


# КЛЮЧЕВОЕ: имя задачи = "ping" (ровно так, как шлёт API)
@celery_app.task(name="ping")
def ping() -> str:
    logger.info("Ping task executed")
    return "pong"
