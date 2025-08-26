from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers.bots import router as bots_router
from app.api.v1.routers.celery_ping import router as celery_router
from app.api.v1.routers.debug import router as debug_router  # наш отладочный пинг/db-check

# Импортируем РОУТЕРЫ НАПРЯМУЮ (без общей "routers" прослойки)
from app.api.v1.routers.health import router as health_router
from app.api.v1.routers.org_users import router as org_users_router
from app.api.v1.routers.organizations import router as organizations_router
from app.api.v1.routers.tasks import router as tasks_router
from app.api.v1.routers.users import router as users_router

app = FastAPI(
    title="TTQ Telegram Platform",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS на локалке и для Swagger
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ВАЖНО: НЕ задаём здесь prefix="/api/v1".
# У каждого модуля внутри уже свой prefix, например "/api/v1/users", "/api/v1/bots", и т.д.
app.include_router(health_router)
app.include_router(celery_router)
app.include_router(organizations_router)
app.include_router(users_router)
app.include_router(bots_router)
app.include_router(org_users_router)
app.include_router(debug_router)
app.include_router(tasks_router)
