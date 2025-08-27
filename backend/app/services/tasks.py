from __future__ import annotations

import time
from typing import Any, Dict

from app.services.celery_app import celery_app


@celery_app.task(name="ping")
def ping() -> Dict[str, Any]:
    return {"pong": True}


@celery_app.task(name="long_demo", bind=True)
def long_demo(self, text: str, steps: int = 3, delay: float = 0.5) -> Dict[str, Any]:
    """
    Демонстрационная задача с прогрессом.
    """
    steps = max(1, int(steps))
    delay = float(delay)

    for i in range(1, steps + 1):
        time.sleep(delay)
        self.update_state(
            state="PROGRESS",
            meta={"progress": {"step": i, "total": steps, "progress_pct": int(i * 100 / steps)}},
        )

    return {
        "original": text,
        "length": len(text),
        "echo": f"Processed '{text}' in {steps} steps",
        "progress": {"step": steps, "total": steps, "progress_pct": 100},
    }
