"""Handler for the help command."""

from aiogram import types
from loader import dp

@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """Provide brief info about the bot and detailed instructions."""
    await message.reply("will write later.")
