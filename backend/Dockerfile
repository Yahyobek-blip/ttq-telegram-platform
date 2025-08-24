FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1     PIP_NO_CACHE_DIR=off     PIP_DISABLE_PIP_VERSION_CHECK=on

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends     build-essential     && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install --upgrade pip && pip install poetry

# Copy project metadata and install
COPY ../pyproject.toml ../README.md ./
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

# Copy sources
COPY . .

EXPOSE 8080