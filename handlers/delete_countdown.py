import logging
from typing import Union
import uuid

from aiogram import types
from aiogram.dispatcher import FSMContext
from apscheduler.jobstores.base import JobLookupError

from loader import dp, sched, supabase
from states.states import MyCountdowns


async def disable_daily_reminders(user_id: int, cd_name: str):
    """Delete scheduled reminders job if it exists.

    Parameters
    ----------
    user_id : int
        Telegram user id
    cd_name : str
        Countdown name
    """

    job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id} {cd_name}"))

    try:
        sched.remove_job(job_id)
    except JobLookupError:
        # daily reminders were not on or the job already reached its end date
        # and deleted itself
        pass


async def delete_countdown(user_id: int, cd_name: str) -> Union[list, None]:
    """Delete specific countdown from db.

    Parameters
    ----------
    user_id : int
        Telegram user id
    cd_name : str
        Countdown name

    Returns
    -------
    Union[list, None]
        List containing deleted row if countdown was found, else None
    """
    data = (
        supabase.table("Countdowns")
        .delete()
        .eq("tg_user_id", user_id)
        .eq("name", cd_name)
        .execute()
    )

    try:
        # data[0] -> what just got deleted
        assert len(data[0]) > 0
    except AssertionError:
        return None
    else:
        return data[0]


async def goodbye_countdown(user_id: int, cd_name: str):
    """Disable countdown reminders and delete countdown from db.

    Parameters
    ----------
    user_id : int
        Telegram user id
    cd_name : str
        Countdown name
    """

    await disable_daily_reminders(user_id, cd_name)

    deleted = await delete_countdown(user_id, cd_name)

    if deleted:
        await dp.bot.send_message(
            user_id, f"Countdown <b>{cd_name}</b> deleted"
        )
    else:
        logging.error(
            f"UNEXPECTED: Delete operation failed. Countdown '{cd_name}' from "
            f"user '{user_id}' not found."
        )
        await dp.bot.send_message(
            user_id,
            "Sorry, I ran into sth unexpected. Please try again later.",
        )


@dp.callback_query_handler(
    text="delete_countdown", state=MyCountdowns.countdown_selected
)
async def confirm_delete(call: types.CallbackQuery, state: FSMContext):
    """Get confirmation to delete a countdown."""
    state_data = await state.get_data()
    cd_name = state_data["cd_name"]

    keyboard = types.InlineKeyboardMarkup(row_width=1)
    buttons = [
        types.InlineKeyboardButton(
            text="Yes", callback_data="delete_confirmed"
        ),
        types.InlineKeyboardButton(
            text="No", callback_data=f"countdown:{cd_name}"
        ),
        types.InlineKeyboardButton(
            text="<< Back to Countdown", callback_data=f"countdown:{cd_name}"
        ),
    ]
    keyboard.add(*buttons)

    await call.message.edit_text(
        text=f"Are you sure you want to delete <b>{cd_name}</b>?",
        reply_markup=keyboard,
    )
    await call.answer()


@dp.callback_query_handler(
    text="delete_confirmed", state=MyCountdowns.countdown_selected
)
async def user_delete_countdown(call: types.CallbackQuery, state: FSMContext):
    """Delete the countdown and all scheduled jobs associated with it.

    Will trigger when user indicates that they want to delete a countdown.
    """

    user_id = call.from_user.id
    state_data = await state.get_data()
    cd_name = state_data["cd_name"]

    await goodbye_countdown(user_id, cd_name)

    job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"bye {user_id} {cd_name}"))

    try:
        sched.remove_job(job_id)
    except JobLookupError:
        logging.exception(
            "UNEXPECTED: User was deleting a countdown and last clean up job "
            "was not found."
        )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton(
            text="<< Back to List", callback_data="back_to_list"
        )
    )

    await call.message.edit_text(
        text=f"You have deleted <b>{cd_name}</b>.", reply_markup=keyboard
    )
    await call.answer()
