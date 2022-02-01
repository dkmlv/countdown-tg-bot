"""Handler for the help command."""

from aiogram import types
from loader import dp


@dp.message_handler(commands="help", state="*")
async def give_help(message: types.Message):
    """Provide brief info about the bot and detailed instructions."""
    help_msg = (
        "<b>What can I do?</b>\n"
        "‣ Create countdowns for anything you want\n"
        "‣ <s>Give you a shot of anxiety every day</s>\n"
        "‣ Send daily countdown reminders\n"
        "‣ Manage all your countdowns\n\n"
        "<b>Instructions:</b>\n"
        "Go to the special commands ☰ <b>Menu</b> and choose the operation "
        "that you want me to perform.\n\n"
        "<b>Available commands:</b>\n"
        "<i>/start</i> - brief info about me\n"
        "<i>/help</i> - instructions on how to interact with me\n"
        "<i>/new_countdown</i> - create a new countdown (can be cancelled "
        "anytime using /cancel)\n"
        "<i>/my_countdowns</i> - manage countdowns (see how much time is "
        "left, edit & delete countdown)\n"
        "<i>/cancel</i> - cancel current operation (if the bot is frozen, "
        "try using this command)\n\n<b>NOTE</b>:\n1 month -> 30.5 days\n"
        "1 year -> 365 days\n\n<b>Source code "
        '<a href="https://github.com/DurbeKK/countdown-tg-bot">here</a></b>'
    )
    await message.reply(help_msg)
