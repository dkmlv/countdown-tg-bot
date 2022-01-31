"""Handler for the start command.

Command behaves differently if user is a first-time user (doesn't exist in db).
User is asked to give their time zone information, which will be used to adjust
the dates and time (if user turns on daily reminders) provided for countdowns.
Time zone information along with user's id is inserted into db.
"""

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from timezonefinder import TimezoneFinder

from loader import dp, supabase
from states.states import Start
from utils.get_coordinates import get_coordinates
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
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(
            types.KeyboardButton(text="Send Location", request_location=True)
        )
        await message.answer(
            "Looks like you are a first-time user.\nTo get started, can you "
            "please send me your location?",
            reply_markup=keyboard,
        )
        await message.answer(
            "I will use your location to find the timezone you're in (only "
            "your timezone information will be stored)."
        )
        await message.answer(
            "Alternatively, you can also provide city name like <code>"
            "Tashkent</code>"
        )
        await Start.waiting_for_tz.set()
    else:
        await message.answer("See <b>/help</b> for more information.")


@dp.message_handler(content_types=["location"], state=Start.waiting_for_tz)
@dp.message_handler(state=Start.waiting_for_tz)
async def add_user(message: types.Message, state: FSMContext):
    """Insert user info to the db if valid time zone is provided."""
    if message.location:
        location = message.location
    else:
        location = get_coordinates(message.text)

    if not location:
        await message.reply(
            "Um, are you sure you typed your city name correctly?"
        )
        return

    longitude, latitude = location["longitude"], location["latitude"]
    tf = TimezoneFinder()
    time_zone = tf.timezone_at(lng=longitude, lat=latitude)

    if time_zone:
        user_info = {
            "tg_user_id": message.from_user.id,
            "time_zone": time_zone,
        }
        supabase.table("Accounts").insert(user_info).execute()
        logging.info("Added new user successfully.")

        await state.finish()
        await message.answer(
            "Thank you, you're all set. Feel free to explore other commands "
            "using <b>/help</b>.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
    else:
        logging.error("UNEXPECTED: couldn't identify time zone with location.")
        await state.finish()
        await message.reply(
            "Operation cancellled. Sorry, I don't understand which timezone "
            "this is.",
            reply_markup=types.ReplyKeyboardRemove(),
        )
