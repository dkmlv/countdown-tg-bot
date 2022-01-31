"""Handler for the new_countdown command.

The process of creating a new countdown is basically:
    1. Ask to choose countdown format
    2. Ask to type name for the countdown
    3. Ask whether user would like to recieve daily reminders
    4. Ask date and time for the countdown
"""

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from handlers.schedule_jobs import schedule_goodbye_cd, schedule_reminders
from loader import dp, supabase
from states.states import NewCountdown
from utils.check_cd_name import check_countdown_name
from utils.get_db_data import get_tz_info
from utils.validate_date import validate_dt


@dp.message_handler(commands="new_countdown", state="*")
@dp.throttled(rate=3)
async def ask_countdown_format(message: types.Message):
    """Ask user to pick a countdown format.

    There will be two countdown formats available:

    1) End of the world
       ----------------
       1 year, 2 months, 3 days, 4 hours, 5 minutes, 6 seconds left

    2) End of the world
       ----------------
       Time left:
       1 year
       2 months
       3 days
       4 hours
       5 minutes
       6 seconds
    """

    await NewCountdown.waiting_for_format.set()

    heading_one = "<b>Format 1</b>\n========\n"
    heading_two = "<b>Format 2</b>\n========\n"
    format_one = "1 year, 2 months, 3 days, 4 hours, 5 minutes, 6 seconds left"
    format_two = (
        "<i>Time left</i>:\n1 year\n2 months\n3 days\n4 hours\n5 minutes\n6 "
        "seconds"
    )

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["1", "2"]
    keyboard.add(*buttons)

    await message.reply(
        f"{heading_one}{format_one}\n\n{heading_two}{format_two}",
    )
    await message.answer(
        f"<b>Please choose a countdown format that you prefer.</b>",
        reply_markup=keyboard,
    )
    await message.answer(
        "Btw, you can cancel current operation anytime using <b>/cancel</b>."
    )


@dp.message_handler(
    Text(equals=["1", "2"]), state=NewCountdown.waiting_for_format
)
async def ask_countdown_name(message: types.Message, state: FSMContext):
    """Ask user for a countdown name."""
    await state.update_data(cd_format=int(message.text))
    await NewCountdown.next()

    await message.answer(
        "What would you like to name the countdown?",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message_handler(state=NewCountdown.waiting_for_name)
async def ask_daily_reminders(message: types.Message, state: FSMContext):
    """Ask preference on daily reminders if valid name is provided.

    User is expected to provide a countdown name. Check to make sure that the
    countdown name is valid. If it's valid, move on and ask about daily
    reminders.
    """

    countdown_name = message.text
    # text will be None if name is valid, str if invalid
    text = await check_countdown_name(message.from_user.id, countdown_name)

    if text:
        await message.reply(text)
    else:
        await state.update_data(cd_name=countdown_name)
        await NewCountdown.next()

        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Yes", "No"]
        keyboard.add(*buttons)

        await message.answer(
            "Would you like to receive daily reminders about how much "
            "time is left till the countdown is up?",
            reply_markup=keyboard,
        )


@dp.message_handler(
    Text(equals=["Yes", "No"]), state=NewCountdown.waiting_for_preference
)
async def ask_countdown_dt(message: types.Message, state: FSMContext):
    """Ask date and time for the countdown."""
    daily_reminders = True if message.text == "Yes" else False
    await state.update_data(reminders=daily_reminders)
    await NewCountdown.next()

    await message.answer(
        "Please send the date and time for the countdown in <b>YYYY-MM-DD "
        "hh:mm</b> format (time in 24 hour format). You should provide a date "
        "and time in the future.\n\n<b>Example:</b> "
        "<code>2030-11-12 15:00</code>",
        reply_markup=types.ReplyKeyboardRemove(),
    )


@dp.message_handler(state=NewCountdown.waiting_for_dt)
async def validate_and_insert(message: types.Message, state: FSMContext):
    """Validate date and time and insert countdown data to db."""
    countdown_dt = message.text
    time_zone = await get_tz_info(message.from_user.id)

    if time_zone:
        utc_dt = await validate_dt(countdown_dt, time_zone)

        if utc_dt:
            user_id = message.from_user.id
            countdown_data = await state.get_data()
            countdown_name = countdown_data["cd_name"]
            countdown_reminders = countdown_data["reminders"]
            countdown_format = countdown_data["cd_format"]

            data = {
                "name": countdown_name,
                "tg_user_id": user_id,
                "date_time": utc_dt,
                "reminders": countdown_reminders,
                "format": countdown_format,
            }

            supabase.table("Countdowns").insert(data).execute()
            logging.info("Countdown created successfully.")

            await message.answer("Yay, countdown created successfully.")
            await state.finish()

            # schedule daily reminders (if user has them on)
            if countdown_reminders:
                await schedule_reminders(
                    user_id, countdown_name, utc_dt, countdown_format
                )

            # schedule clean up job to run when countdown is over
            await schedule_goodbye_cd(user_id, countdown_name, utc_dt)

        else:
            await message.reply(
                "Um, are you sure you typed the date correctly? Please double "
                "check that you provided a future date and time in the "
                "correct format and try again."
            )
    else:
        await state.finish()
        await message.reply(
            "Looks you did not set up your time zone at the start, so I'll "
            "abort this operation. Please use <b>/start</b> and try again."
        )
