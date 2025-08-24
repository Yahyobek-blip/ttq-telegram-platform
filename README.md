# Telegram Presence Platform — Stage 0 (Base)

This is a minimal Stage 0 skeleton: repo layout, tooling, envs, logging to JSON, Docker Compose (Postgres, Redis, backend, worker), and CI.

## Layout
```
backend/
  app/
    core/            # config, logging
    api/v1/routers/  # FastAPI routers
    services/        # celery app
frontend/            # reserved
ops/                 # reserved
.github/workflows/   # CI
```

## Quickstart (local)
```bash
# 1) Create & activate venv (Python 3.11+)
python -m venv .venv
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# 2) Install Poetry
pip install --upgrade pip
pip install poetry

# 3) Install deps
poetry install --with dev

# 4) Pre-commit hooks
pre-commit install
pre-commit run --all-files

# 5) Run backend
uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

# 6) Healthcheck
curl http://127.0.0.1:8080/api/v1/health
```

## Docker Compose
```bash
# copy env
cp .env.dev .env
docker compose up --build
# backend: http://127.0.0.1:8080/api/v1/health
```

## CI
GitHub Actions runs: ruff, black, isort, mypy, tests, docker build.