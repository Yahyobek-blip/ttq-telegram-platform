# backend/app/adapters/telegram/run.py
import asyncio
import logging

from aiogram import Bot, Dispatcher

from app.adapters.telegram.bot import router
from app.core.config import settings

logger = logging.getLogger("tg_bot")


async def main():
    logger.info("Starting aiogram bot...")
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
