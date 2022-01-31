"""Handler for the my_countdown command.

Using this command users can choose a countdown of their choice and:
    1. Show countdown
    2. Edit countdown
    3. Delete countdown
"""

from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp
from states.states import MyCountdowns
from utils.get_db_data import get_countdown_names


@dp.message_handler(commands="my_countdowns", state="*")
@dp.callback_query_handler(text="back_to_list", state="*")
@dp.throttled(rate=3)
async def ask_to_pick_countdown(
    entity: Union[types.Message, types.CallbackQuery], state: FSMContext
):
    """Ask the user to pick a countdown."""
    if type(entity) == types.CallbackQuery:
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
            "You have no countdowns set up. To create a new countdown, use "
            "<b>/new_countdown</b>"
        )
    elif type(entity) == types.CallbackQuery:
        await entity.message.edit_text(  # type: ignore
            "You have no countdowns set up. To create a new countdown, use "
            "<b>/new_countdown</b>"
        )
        await entity.answer()  # type: ignore


@dp.callback_query_handler(
    text_startswith="countdown:", state=[None, MyCountdowns.countdown_selected]
)
async def ask_what_to_do(call: types.CallbackQuery, state: FSMContext):
    """Ask user what operation to perform on the selected countdown."""
    countdown_name = call.data.split(":")[1]

    await MyCountdowns.countdown_selected.set()
    await state.update_data(cd_name=countdown_name)

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    buttons = [
        types.InlineKeyboardButton(
            text="Show Countdown", callback_data=f"show_countdown"
        ),
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

    # first button occupies whole row
    keyboard.add(buttons[0])
    keyboard.add(*buttons[1:3])
    # last button occupies whole row
    keyboard.add(buttons[3])

    await call.message.edit_text(
        f"Great, you selected <b>{countdown_name}</b>.\nWhat do you want me "
        "do with this countdown?",
        reply_markup=keyboard,
    )
    await call.answer()
