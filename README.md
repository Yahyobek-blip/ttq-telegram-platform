# TTQ Telegram Platform

Production-ready skeleton for a managed Telegram platform.

**Stack:** FastAPI · SQLAlchemy · Alembic · PostgreSQL · Celery/Redis · aiogram · Docker Compose
**Stage 0–1 готово:** базовая инфраструктура, health-check’и, CRUD по organizations/users/bots/org-users, Celery ping, телеграм-бот (aiogram 3.x).

## Быстрый старт

```bash
cp .env.example .env.dev
docker compose up -d --build
# хелсчеки
curl http://127.0.0.1:8080/api/v1/health
curl http://127.0.0.1:8080/api/v1/health/db
API (чекпоинты)
GET /api/v1/health, GET /api/v1/health/db

GET/POST/PATCH/DELETE /api/v1/organizations

GET/POST/PATCH/DELETE /api/v1/users

GET/POST/PATCH/DELETE /api/v1/bots

GET/POST/PATCH/DELETE /api/v1/org-users

POST /api/v1/celery/ping — ставит задачу, worker отвечает "pong"

План Stage 2 (next)
Логин/авторизация для админки (JWT / session)

Связка бота с организациями, валидации

Базовая админ-панель (frontend)

Интеграционные тесты и CI

## Этапы разработки
- [stage-0-init](https://github.com/ТВОЙ_ЮЗЕР/ttq-telegram-platform/tree/stage-0-init) → Инициализация проекта, базовые настройки
- [stage-1-infrastructure](https://github.com/ТВОЙ_ЮЗЕР/ttq-telegram-platform/tree/stage-1-infrastructure) → Инфраструктура: Docker, база данных, проверки работоспособности
- [stage-2-backend-tg-bot](https://github.com/ТВОЙ_ЮЗЕР/ttq-telegram-platform/tree/stage-2-backend-tg-bot) → Бэкенд для Telegram-бота
