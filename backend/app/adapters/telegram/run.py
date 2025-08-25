import asyncio
import logging
import signal

from app.adapters.telegram.bot import bot, dp

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s | %(message)s")


async def _main() -> None:
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


def _graceful_shutdown(loop: asyncio.AbstractEventLoop):
    for task in asyncio.all_tasks(loop):
        task.cancel()


if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, _graceful_shutdown, loop)
    try:
        loop.run_until_complete(_main())
    finally:
        loop.run_until_complete(bot.session.close())
        loop.close()
