from fastapi import FastAPI, Request

from .api.v1.routers.health import router as health_router
from .core.logging_config import setup_logging

setup_logging()

app = FastAPI(title="TTQ Telegram Presence Platform")


@app.middleware("http")
async def add_request_id_header(request: Request, call_next):
    # Very lightweight request id
    import uuid

    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.include_router(health_router, prefix="/api/v1")
