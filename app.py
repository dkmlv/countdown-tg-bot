from aiogram import executor

import handlers
from loader import dp
from utils.notify_admin import notify_on_startup
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    """Set default commands for the bot and notify of bot startup."""
    await set_default_commands(dispatcher)
    await notify_on_startup(dispatcher)


if __name__ == "__main__":
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
