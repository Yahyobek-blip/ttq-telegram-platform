import json
import logging
import os
from logging.config import dictConfig
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcnow().isoformat(timespec="milliseconds") + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            # Common correlation fields (populate via extra=... where applicable)
            "request_id": getattr(record, "request_id", None),
            "user_id": getattr(record, "user_id", None),
            "org_id": getattr(record, "org_id", None),
            "team_id": getattr(record, "team_id", None),
            "entity": getattr(record, "entity", None),
            "entity_id": getattr(record, "entity_id", None),
            "action": getattr(record, "action", None),
            "status": getattr(record, "status", None),
            "error_code": getattr(record, "error_code", None),
            "latency_ms": getattr(record, "latency_ms", None),
            "retries": getattr(record, "retries", None),
            "trace_id": getattr(record, "trace_id", None),
        }
        return json.dumps(payload, ensure_ascii=False)

def setup_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_json = os.getenv("LOG_JSON", "1") in ("1", "true", "True")
    log_file = os.getenv("LOG_FILE", "logs/app.log")

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    fmt = "JSON" if log_json else "%(asctime)s %(levelname)s %(name)s %(message)s"

    base_handlers = {
        "console": {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "json" if log_json else "plain",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json" if log_json else "plain",
            "filename": log_file,
            "maxBytes": 5_000_000,
            "backupCount": 3,
            "encoding": "utf-8",
        },
    }

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "json": {"()": JSONFormatter},
                "plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"},
            },
            "handlers": base_handlers,
            "root": {"level": log_level, "handlers": ["console", "file"]},
        }
    )