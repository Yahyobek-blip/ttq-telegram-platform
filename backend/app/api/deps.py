from __future__ import annotations

from app.db.session import get_db  # просто реэкспорт, чтобы не менять импорты в роутерах

__all__ = ["get_db"]
