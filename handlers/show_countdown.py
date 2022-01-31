"""Show countdown operation is handled here."""

import logging

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states.states import MyCountdowns
from utils.calculate_diff import calculate_diff
from utils.get_db_data import get_countdown_details
from utils.send_message import send_message


async def send_countdown_details(
    user_id: int, cd_name: str, date_time: str, cd_format: int
):
    """Send how much time is left till the countdown is up.

    Parameters
    ----------
    user_id : int
        Telegram user id to whom the details should be sent
    cd_name : str
        Name of the countdown
    date_time : str
        Countdown date and time (in the '%Y-%m-%dT%H:%M:%S%z' format)
    cd_format : int
        The format in which to send the countdown details
    """

    time_diff = calculate_diff(date_time)

    text_divider = "=" * len(cd_name)

    text = f"<b>{cd_name}</b>\n{text_divider}\n"

    if cd_format == 1:
        text += f"{time_diff} left"
    else:
        text += "<i>Time left:</i>\n"
        time_diff_list = time_diff.split(", ")

        # last item may be like -> 5 minutes and 6 seconds
        if "and" in time_diff_list[-1]:
            time_diff_list[-1:] = time_diff_list[-1].split(" and ")

        for item in time_diff_list:
            text += f"{item}\n"

    await send_message(user_id, text)


@dp.callback_query_handler(
    text="show_countdown", state=MyCountdowns.countdown_selected
)
async def show_countdown(call: types.CallbackQuery, state: FSMContext):
    """Update user on how much time is left till the countdown is up."""
    user_id = call.from_user.id

    state_data = await state.get_data()
    countdown_name = state_data["cd_name"]

    countdown_data = await get_countdown_details(user_id, countdown_name)

    if not countdown_data:
        logging.error(
            "UNEXPECTED: Show Countdown operation failed. Countdown not found."
        )
        await call.message.answer(
            "Sorry, I couldn't get countdown details. Please try again later."
        )
    else:
        countdown_dt = countdown_data["date_time"]
        countdown_format = countdown_data["format"]

        await send_countdown_details(
            user_id, countdown_name, countdown_dt, countdown_format
        )

    await call.answer()
