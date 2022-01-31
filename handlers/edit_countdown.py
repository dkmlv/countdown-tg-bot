"""Edit countdown operations are all done here. Sorry for the mess."""

import datetime as dt
import logging
import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext

from aiogram.utils.emoji import emojize
from handlers.delete_countdown import disable_cleanup, disable_daily_reminders
from handlers.schedule_jobs import schedule_goodbye_cd, schedule_reminders
from loader import dp, sched, supabase
from states.states import MyCountdowns
from utils.check_cd_name import check_countdown_name
from utils.convert_dt import convert_dt
from utils.get_db_data import get_countdown_details, get_tz_info
from utils.validate_date import validate_dt


@dp.callback_query_handler(
    text="edit_countdown", state=MyCountdowns.countdown_selected
)
async def ask_what_to_edit(call: types.CallbackQuery, state: FSMContext):
    """Ask what specific countdown information to edit."""
    # let the user know that its loading and not stuck
    await call.message.edit_text(emojize(":hourglass_flowing_sand:"))

    user_id = call.from_user.id
    state_data = await state.get_data()
    countdown_name = state_data["cd_name"]

    countdown_data = await get_countdown_details(user_id, countdown_name)

    if not countdown_data:
        logging.error(
            "UNEXPECTED: Edit Countdown operation failed. Countdown not found."
        )
        await call.message.answer(
            "Sorry, I couldn't get countdown details. Please try again later."
        )
    else:
        countdown_dt = countdown_data["date_time"]
        countdown_in_users_tz = await convert_dt(user_id, countdown_dt)

        countdown_format = countdown_data["format"]
        if countdown_format == 1:
            format_data = "change_format_to:2"
        else:
            format_data = "change_format_to:1"

        countdown_reminders = countdown_data["reminders"]

        if countdown_reminders:
            reminders_text = "Turn Reminders OFF"
            reminders_data = "turn_reminders_off"
            countdown_reminders = "ON"
        else:
            reminders_text = "Turn Reminders ON"
            reminders_data = "turn_reminders_on"
            countdown_reminders = "OFF"

        text = (
            "What information do you want me to edit?\n\n"
            f"<b>Name</b>: {countdown_name}\n"
            f"<b>DateTime</b>: {countdown_in_users_tz}\n"
            f"<b>Format</b>: {countdown_format}\n"
            f"<b>Reminders</b>: {countdown_reminders}\n"
        )

        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = [
            types.InlineKeyboardButton(
                text="Edit Name", callback_data="edit_name"
            ),
            types.InlineKeyboardButton(
                text="Edit DateTime", callback_data="edit_dt"
            ),
            types.InlineKeyboardButton(
                text="Change Format", callback_data=format_data
            ),
            types.InlineKeyboardButton(
                text=reminders_text, callback_data=reminders_data
            ),
            types.InlineKeyboardButton(
                text="<< Back to Countdown",
                callback_data=f"countdown:{countdown_name}",
            ),
        ]
        keyboard.add(*buttons)

        await call.message.edit_text(text=text, reply_markup=keyboard)

    await call.answer()


@dp.callback_query_handler(
    text="edit_name", state=MyCountdowns.countdown_selected
)
async def ask_new_countdown_name(call: types.CallbackQuery):
    """Ask user to input a new countdown name."""
    await MyCountdowns.edit_name.set()

    await call.message.edit_text(
        "What would you like to change the countdown name to?"
    )
    await call.answer()


@dp.message_handler(state=MyCountdowns.edit_name)
async def update_countdown_name(message: types.Message, state: FSMContext):
    """Update countdown name if valid new name is provided.

    Since scheduler job ids are also generated using the countdown name, they
    are deleted and added back (can't modify job ids).
    """

    user_id = message.from_user.id
    new_countdown_name = message.text
    # text will be None if name is valid, str if invalid
    text = await check_countdown_name(user_id, new_countdown_name)

    if text:
        await message.reply(text)
    else:
        logging.info("Editing countdown name")

        state_data = await state.get_data()
        old_countdown_name = state_data["cd_name"]

        data = (
            supabase.table("Countdowns")
            .update({"name": new_countdown_name})
            .eq("tg_user_id", user_id)
            .eq("name", old_countdown_name)
            .execute()
        )

        countdown_data = data[0][0]
        countdown_dt = countdown_data["date_time"]
        countdown_reminders = countdown_data["reminders"]
        countdown_format = countdown_data["format"]

        if countdown_reminders:
            await disable_daily_reminders(user_id, old_countdown_name)
            await schedule_reminders(
                user_id, new_countdown_name, countdown_dt, countdown_format
            )

        await disable_cleanup(user_id, old_countdown_name)
        await schedule_goodbye_cd(user_id, new_countdown_name, countdown_dt)

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text="<< Back to List", callback_data="back_to_list"
            )
        )

        await state.finish()
        await message.answer(
            "You got it! Name updated.", reply_markup=keyboard
        )


@dp.callback_query_handler(
    text="edit_dt", state=MyCountdowns.countdown_selected
)
async def ask_new_countdown_dt(call: types.CallbackQuery):
    """Ask user for a new countdown date and time."""
    await MyCountdowns.edit_dt.set()
    await call.message.edit_text(
        "Please send the date and time for the countdown in <b>YYYY-MM-DD "
        "hh:mm</b> format (time in 24 hour format). You should provide a date "
        "and time in the future.\n\n<b>Example:</b> "
        "<code>2030-11-12 15:00</code>"
    )
    await call.answer()


@dp.message_handler(state=MyCountdowns.edit_dt)
async def update_countdown_dt(message: types.Message, state: FSMContext):
    """Validate date and time and update countdown date and time.

    Scheduled jobs are modified to reflect the new date and time.
    """

    countdown_dt = message.text
    time_zone = await get_tz_info(message.from_user.id)

    # to create a countdown, tz info is required so it cant be None rn
    assert time_zone is not None

    utc_dt = await validate_dt(countdown_dt, time_zone)

    if utc_dt:
        user_id = message.from_user.id
        state_data = await state.get_data()
        countdown_name = state_data["cd_name"]

        data = (
            supabase.table("Countdowns")
            .update({"date_time": utc_dt})
            .eq("tg_user_id", user_id)
            .eq("name", countdown_name)
            .execute()
        )

        countdown_data = data[0][0]
        countdown_dt = countdown_data["date_time"]
        countdown_reminders = countdown_data["reminders"]
        cd_format = countdown_data["format"]

        dt_format = "%Y-%m-%dT%H:%M:%S%z"
        dt_obj = dt.datetime.strptime(countdown_dt, dt_format)

        if countdown_reminders:
            job_id = str(
                uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id} {countdown_name}")
            )
            sched.modify_job(
                job_id, args=[user_id, countdown_name, countdown_dt, cd_format]
            )
            sched.reschedule_job(
                job_id,
                trigger="cron",
                day="*",
                hour=dt_obj.hour,
                minute=dt_obj.minute,
                end_date=dt_obj,
                timezone="UTC",
            )

        # countdown will be up. if user has reminders on, last reminder should
        # be delivered by this time unless sth went wrong.
        run_dt = dt_obj + dt.timedelta(seconds=10)

        job_id = str(
            uuid.uuid5(uuid.NAMESPACE_DNS, f"bye {user_id} {countdown_name}")
        )

        sched.reschedule_job(
            job_id,
            trigger="date",
            run_date=run_dt,
        )

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                text="<< Back to List", callback_data="back_to_list"
            )
        )

        logging.info("Modified countdown datetime successfully.")
        await state.finish()
        await message.answer(
            "You got it! Date and time updated.", reply_markup=keyboard
        )

    else:
        await message.reply(
            "Um, are you sure you typed the date correctly? Please double "
            "check that you provided a future date and time in the "
            "correct format and try again."
        )


@dp.callback_query_handler(
    text_startswith="change_format_to:", state=MyCountdowns.countdown_selected
)
async def update_cd_format(call: types.CallbackQuery, state: FSMContext):
    """Change countdown format to the other one.

    If daily reminders are on, modify job to use the new format.
    """

    user_id = call.from_user.id
    state_data = await state.get_data()
    countdown_name = state_data["cd_name"]
    cd_format = call.data.split(":")[-1]

    data = (
        supabase.table("Countdowns")
        .update({"format": cd_format})
        .eq("tg_user_id", user_id)
        .eq("name", countdown_name)
        .execute()
    )

    countdown_data = data[0][0]
    countdown_dt = countdown_data["date_time"]
    countdown_reminders = countdown_data["reminders"]

    if countdown_reminders:
        job_id = str(
            uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id} {countdown_name}")
        )
        sched.modify_job(
            job_id, args=[user_id, countdown_name, countdown_dt, cd_format]
        )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="<< Back to List", callback_data="back_to_list"
        )
    )

    logging.info("Modified countdown format successfully.")
    await state.finish()
    await call.message.edit_text(
        f"You got it! Format changed to {cd_format}.", reply_markup=keyboard
    )
    await call.answer()


@dp.callback_query_handler(
    text="turn_reminders_on", state=MyCountdowns.countdown_selected
)
async def turn_reminders_on(call: types.CallbackQuery, state: FSMContext):
    """Turn daily reminders on for specific countdown."""
    user_id = call.from_user.id
    state_data = await state.get_data()
    countdown_name = state_data["cd_name"]

    data = (
        supabase.table("Countdowns")
        .update({"reminders": True})
        .eq("tg_user_id", user_id)
        .eq("name", countdown_name)
        .execute()
    )

    countdown_data = data[0][0]
    countdown_dt = countdown_data["date_time"]
    countdown_format = countdown_data["format"]

    await schedule_reminders(
        user_id, countdown_name, countdown_dt, countdown_format
    )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="<< Back to List", callback_data="back_to_list"
        )
    )

    await state.finish()
    await call.message.edit_text(
        "You got it! Reminders are ON.", reply_markup=keyboard
    )
    await call.answer()


@dp.callback_query_handler(
    text="turn_reminders_off", state=MyCountdowns.countdown_selected
)
async def turn_reminders_off(call: types.CallbackQuery, state: FSMContext):
    """Turn daily reminders off for specific countdown."""
    user_id = call.from_user.id
    state_data = await state.get_data()
    countdown_name = state_data["cd_name"]

    _ = (
        supabase.table("Countdowns")
        .update({"reminders": False})
        .eq("tg_user_id", user_id)
        .eq("name", countdown_name)
        .execute()
    )
    await disable_daily_reminders(user_id, countdown_name)

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="<< Back to List", callback_data="back_to_list"
        )
    )

    await state.finish()
    await call.message.edit_text(
        "You got it! Reminders are OFF.", reply_markup=keyboard
    )
    await call.answer()
