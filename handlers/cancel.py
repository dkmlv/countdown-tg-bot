"""Handler for the cancel command.

Can be used anytime to reset the state and remove reply keyboard.
"""

from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import dp


@dp.message_handler(commands="cancel", state="*")
async def reset_state(message: types.Message, state: FSMContext):
    """Cancel current operation (reset the state)."""
    await state.finish()
    await message.reply(
        "No problem, current operation cancelled.",
        reply_markup=types.ReplyKeyboardRemove(),
    )
