from aiogram import executor

import handlers
from handlers.schedule_jobs import schedule_all
from loader import dp, sched
from utils.notify_admin import notify_on_shutdown, notify_on_startup
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    """Set default commands for the bot and notify of bot startup."""
    await set_default_commands(dispatcher)
    # recreate jobs for the apscheduler
    await schedule_all()
    await notify_on_startup(dispatcher)


async def on_shutdown(dispatcher):
    await notify_on_shutdown(dispatcher)
    sched.shutdown()


if __name__ == "__main__":
    executor.start_polling(
        dp, on_startup=on_startup, on_shutdown=on_shutdown, skip_updates=True
    )
