"""Handler for the start command.

Command behaves differently if user is a first-time user (doesn't exist in db).
User is asked to give their time zone information, which will be used to adjust
the dates and time (if user turns on daily reminders) provided for countdowns.
Time zone information along with user's id is inserted into db.
"""

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from dateutil.zoneinfo import get_zonefile_instance

from loader import dp, supabase
from states.states import Start
from utils.get_db_data import get_tz_info


@dp.message_handler(commands="start", state="*")
@dp.throttled(rate=3)
async def greet_user(message: types.Message):
    """Greet user and ask their time zone if they don't exist in db."""
    await message.reply(
        "Hello there, my name is <b>Mirai</b> and I can help you create "
        "countdowns for your events/goals."
    )

    time_zone = await get_tz_info(message.from_user.id)

    if not time_zone:
        await message.answer(
            "Looks like you are a first-time user.\nTo get started, can you "
            "please type your time zone?\nYou can find a list of time zones "
            "here: https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
            "\n\nFor example: If you live in Uzbekistan, just type "
            "'<code>Asia/Tashkent</code>'"
        )
        await Start.waiting_for_tz.set()
    else:
        await message.answer("See <b>/help</b> for more information.")


@dp.message_handler(state=Start.waiting_for_tz)
async def add_user(message: types.Message, state: FSMContext):
    """Insert user info to the db if valid time zone is provided."""
    time_zone = message.text
    zonenames = list(get_zonefile_instance().zones)

    if time_zone in zonenames:
        user_info = {
            "tg_user_id": message.from_user.id,
            "time_zone": time_zone,
        }
        supabase.table("Accounts").insert(user_info).execute()
        logging.info("Added new user successfully.")

        await state.finish()
        await message.answer(
            "Thank you, you're all set. Feel free to explore other commands "
            "like <b>/new_countdown</b> or <b>/help</b>."
        )
    else:
        await message.reply(
            "Sorry, I don't understand which timezone this is. Are you sure "
            "you typed it correctly?"
        )
