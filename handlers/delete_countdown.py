import logging
from typing import Union
import uuid

from apscheduler.jobstores.base import JobLookupError

from loader import dp, sched, supabase


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
