import datetime as dt
import logging

from aiogram import types
from aiogram.dispatcher import FSMContext
from dateutil import tz

from loader import dp, sched, supabase
from states.states import MyCountdowns
from utils.get_db_data import get_countdown_details, get_tz_info


@dp.callback_query_handler(
    text="edit_countdown", state=MyCountdowns.countdown_selected
)
async def ask_what_to_edit(call: types.CallbackQuery, state: FSMContext):
    """Ask what specific countdown information to edit."""
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

        countdown_dt = dt.datetime.strptime(
            countdown_dt, "%Y-%m-%dT%H:%M:%S%z"
        )
        users_tz_str = await get_tz_info(user_id)
        # countdown cant be created unless theres tz info available
        # thus users_tz_str should not be None
        assert users_tz_str is not None

        users_tz = tz.gettz(users_tz_str)
        countdown_in_users_tz = countdown_dt.astimezone(users_tz).strftime(
            "%Y-%m-%d %H:%M"
        )

        countdown_format = countdown_data["format"]
        countdown_reminders = countdown_data["reminders"]

        if countdown_reminders:
            countdown_reminders = "ON"
        else:
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
                text="Edit Format", callback_data="edit_format"
            ),
            types.InlineKeyboardButton(
                text="Edit Reminders", callback_data="edit_reminders"
            ),
            types.InlineKeyboardButton(
                text="<< Back to List", callback_data="back_to_list"
            ),
        ]
        keyboard.add(*buttons)

        await call.message.edit_text(text=text, reply_markup=keyboard)

    await call.answer()
