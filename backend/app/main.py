# backend/app/main.py
from fastapi import FastAPI

from app.api.v1.routers import bots, celery_ping, health, org_users, organizations, users

app = FastAPI(title="TTQ_02")

# Роуты
app.include_router(organizations.router, prefix="/api/v1")
app.include_router(celery_ping.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")

app.include_router(users.router, prefix="/api/v1")
app.include_router(bots.router, prefix="/api/v1")
app.include_router(org_users.router, prefix="/api/v1")
