FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip && pip install poetry

# 1) метаданные + deps без установки проекта
COPY pyproject.toml README.md ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 2) исходники бэкенда
COPY backend/ ./backend/

# 3) alembic-файлы
COPY alembic.ini ./alembic.ini
COPY alembic/ ./alembic/

# safety: пакет app присутствует
RUN test -f backend/app/__init__.py || (mkdir -p backend/app && printf "" > backend/app/__init__.py)

# 4) установка текущего проекта (root)
RUN poetry install --no-interaction --no-ansi

EXPOSE 8080
