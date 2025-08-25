import logging
import os

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from celery.result import AsyncResult

from app.services.celery_app import celery_app
from app.services.tasks import ping as ping_task

logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
if not TELEGRAM_TOKEN:
    logger.warning("TELEGRAM_TOKEN is empty. Bot will not start.")

bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(
        "👋 Привет! Я бот TTQ_02. Команда /start работает.\n"
        "Доступно:\n"
        "• /ping — поставить задачу Celery\n"
        "• /task <code>&lt;id&gt;</code> — статус задачи."
    )


@dp.message(Command("ping"))
async def ping_cmd(message: Message) -> None:
    task = ping_task.delay()
    await message.answer(
        f"🟢 Поставил задачу Celery: <code>{task.id}</code>\n"
        f"Проверь статус: <code>/task {task.id}</code>"
    )


@dp.message(Command("task"))
async def task_status(message: Message) -> None:
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.answer("ℹ️ Использование: <code>/task &lt;task_id&gt;</code>")
        return
    task_id = parts[1].strip()
    res = AsyncResult(task_id, app=celery_app)
    if res.successful():
        await message.answer(
            f"✅ <b>{task_id}</b>\nstate: <code>{res.state}</code>\nresult: <code>{res.result}</code>"
        )
    elif res.failed():
        await message.answer(f"❌ <b>{task_id}</b>\nstate: <code>{res.state}</code>")
    else:
        await message.answer(f"⏳ <b>{task_id}</b>\nstate: <code>{res.state}</code>")


@dp.message(F.text)
async def echo(message: Message) -> None:
    await message.answer(f"Ты написал: <code>{message.text}</code>")
