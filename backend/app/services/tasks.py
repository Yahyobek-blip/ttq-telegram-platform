from __future__ import annotations

import time
from typing import Any, Dict

from celery import shared_task


@shared_task(name="ping")
def ping() -> str:
    return "pong"


@shared_task(bind=True, name="long_demo")
def long_demo(self, text: str, steps: int = 5, delay: float = 1.0) -> Dict[str, Any]:
    """
    Демонстрационная долгая задача.
    Обновляет прогресс через self.update_state(...).
    В финале дублирует прогресс внутри итогового result, чтобы статус-ручка могла его показать.
    """
    steps = max(1, int(steps))
    delay = float(delay)

    for i in range(1, steps + 1):
        time.sleep(delay)
        progress_pct = int(i * 100 / steps)
        self.update_state(
            state="PROGRESS",
            meta={"step": i, "total": steps, "progress_pct": progress_pct},
        )

    # Финальный прогресс
    final_progress = {"step": steps, "total": steps, "progress_pct": 100}
    self.update_state(state="PROGRESS", meta=final_progress)

    result: Dict[str, Any] = {
        "original": text,
        "length": len(text or ""),
        "echo": f"Processed '{text}' in {steps} steps",
        # Дублируем прогресс в итог, потому что res.info на SUCCESS = result
        "progress": final_progress,
    }
    return result
