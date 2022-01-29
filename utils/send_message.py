import asyncio
import logging

from aiogram.utils import exceptions

from loader import dp


async def send_message(user_id: int, text: str):
    """Send a message to the user on Telegram.

    Parameters
    ----------
    user_id : int
        Telegram user id to whom the message should be sent
    text: str
        Text to send
    """

    try:
        await dp.bot.send_message(user_id, text)
    except exceptions.BotBlocked:
        logging.error(f"Target [ID:{user_id}]: blocked by user")
    except exceptions.RetryAfter as e:
        logging.error(
            f"Target [ID:{user_id}]: Flood limit is exceeded. Sleep {e.timeout} seconds."
        )
        await asyncio.sleep(e.timeout)
        return await send_message(user_id, text)  # Recursive call
    except exceptions.UserDeactivated:
        logging.error(f"Target [ID:{user_id}]: user is deactivated")
    except exceptions.TelegramAPIError:
        logging.exception(f"Target [ID:{user_id}]: failed")
    else:
        logging.info(f"Target [ID:{user_id}]: success.")
