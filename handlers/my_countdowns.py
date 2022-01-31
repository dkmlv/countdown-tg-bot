"""Handler for the my_countdown command.

Using this command users can choose a countdown of their choice and:
    1. Show countdown
    2. Edit countdown
    3. Delete countdown
"""

import logging
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.utils.emoji import emojize

from handlers.show_countdown import send_countdown_details
from loader import dp
from states.states import MyCountdowns
from utils.get_db_data import get_countdown_details, get_countdown_names


@dp.message_handler(commands="my_countdowns", state="*")
@dp.callback_query_handler(text="back_to_list", state="*")
@dp.throttled(rate=3)
async def ask_to_pick_countdown(
    entity: Union[types.Message, types.CallbackQuery], state: FSMContext
):
    """Ask the user to pick a countdown."""
    if type(entity) == types.CallbackQuery:
        # let the user know that its loading and not stuck
        await entity.message.edit_text(emojize(":hourglass_flowing_sand:"))  # type: ignore
        await state.finish()

    countdown_names = await get_countdown_names(entity.from_user.id)

    if countdown_names:
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []

        for name in countdown_names:
            buttons.append(
                types.InlineKeyboardButton(
                    text=name, callback_data=f"countdown:{name}"
                )
            )

        keyboard.add(*buttons)

        if type(entity) == types.Message:
            await entity.reply(  # type: ignore
                "Please choose a countdown:", reply_markup=keyboard
            )
        elif type(entity) == types.CallbackQuery:
            await entity.message.edit_text(  # type: ignore
                "Please choose a countdown:", reply_markup=keyboard
            )
            await entity.answer()  # type: ignore

    elif type(entity) == types.Message:
        await entity.answer(  # type: ignore
            "You have no countdowns set up.\nTo create one, use "
            "<b>/new_countdown</b>"
        )
    elif type(entity) == types.CallbackQuery:
        await entity.message.edit_text(  # type: ignore
            "You have no countdowns set up.\nTo create one, use "
            "<b>/new_countdown</b>"
        )
        await entity.answer()  # type: ignore


@dp.callback_query_handler(
    text_startswith="countdown:", state=[None, MyCountdowns.countdown_selected]
)
async def present_countdown(call: types.CallbackQuery, state: FSMContext):
    """Present selected countdown with options on what to do with it."""
    # let the user know that its loading and not stuck
    await call.message.edit_text(emojize(":hourglass_flowing_sand:"))

    user_id = call.from_user.id
    countdown_name = call.data.split(":")[1]

    await MyCountdowns.countdown_selected.set()
    await state.update_data(cd_name=countdown_name)

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

        text = await send_countdown_details(
            user_id,
            countdown_name,
            countdown_dt,
            countdown_format,
            scheduled=False,
        )

        keyboard = types.InlineKeyboardMarkup(row_width=2)

        buttons = [
            types.InlineKeyboardButton(
                text="Edit Countdown", callback_data=f"edit_countdown"
            ),
            types.InlineKeyboardButton(
                text="Delete Countdown", callback_data=f"delete_countdown"
            ),
            types.InlineKeyboardButton(
                text="<< Back to List", callback_data=f"back_to_list"
            ),
        ]

        keyboard.add(*buttons[0:-1])
        # last button occupies whole row
        keyboard.add(buttons[-1])

        await call.message.edit_text(
            text=text,  # type: ignore
            reply_markup=keyboard,
        )

    await call.answer()
