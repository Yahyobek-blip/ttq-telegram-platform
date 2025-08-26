# tg_bot/app/adapters/telegram/run.py
from __future__ import annotations

import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from app.adapters.telegram.bot import router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("tg_bot")


async def main() -> None:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN не задан")

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)

    logger.info("Starting aiogram bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
