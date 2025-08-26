# mypy: ignore-errors
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

# ВАЖНО: Base берём из app.db.models.base, а НЕ из session.py
from app.db.models.base import Base


class Bot(Base):
    __tablename__ = "bots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # username нашей учётки бота (уникальный, индекс)
    username = Column(String(64), nullable=False, unique=True, index=True)

    # Telegram bot id (может быть NULL, пока не привязан)
    tg_bot_id = Column(BigInteger, nullable=True, index=True)

    # Привязка к организации (NULL допустим)
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Флаг активности в нашей системе
    is_active = Column(Boolean, nullable=False, server_default=sa.text("true"), default=True)

    # Метаданные токена (сам токен НЕ храним)
    token_hash = Column(String(64), nullable=True)  # sha256(token [+ salt])
    token_last4 = Column(String(8), nullable=True)  # последние 4 символа для визуальной проверки
    token_rotated_at = Column(DateTime(timezone=True), nullable=True)

    # Отношения
    organization = relationship("Organization", backref="bots")

    # helper: проставить метаданные токена
    def set_token_meta(self, token_hash: str, last4: str) -> None:
        self.token_hash = token_hash
        self.token_last4 = last4
        self.token_rotated_at = datetime.now(timezone.utc)
