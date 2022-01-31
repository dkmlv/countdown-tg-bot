"""Job scheduling is mainly done here."""

import datetime as dt
import logging
import uuid

from handlers.delete_countdown import goodbye_countdown
from handlers.show_countdown import send_countdown_details
from loader import sched
from utils.get_db_data import get_all_countdowns


async def schedule_reminders(
    user_id: int, cd_name: str, date_time: str, cd_format: int
):
    """Schedule daily reminders for a specific user.

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

    dt_format = "%Y-%m-%dT%H:%M:%S%z"
    dt_obj = dt.datetime.strptime(date_time, dt_format)

    job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"{user_id} {cd_name}"))

    sched.add_job(
        send_countdown_details,
        args=[user_id, cd_name, date_time, cd_format],
        trigger="cron",
        id=job_id,
        day="*",
        hour=dt_obj.hour,
        minute=dt_obj.minute,
        end_date=dt_obj,
        timezone="UTC",
        replace_existing=True,
        misfire_grace_time=3600,  # max one hour late
    )
    logging.info("Daily reminders scheduled successfully.")


async def schedule_goodbye_cd(user_id: int, cd_name: str, date_time):
    """Schedule clean up to run when the countdown has ended.

    Clean up is just deleting the countdown information from db and deleting
    reminders job if it still exists.

    Parameters
    ----------
    user_id : int
        Telegram user id
    cd_name : str
        Countdown name
    date_time: str
        Countdown date and time (in the '%Y-%m-%dT%H:%M:%S%z' format)
    """

    dt_format = "%Y-%m-%dT%H:%M:%S%z"
    dt_obj = dt.datetime.strptime(date_time, dt_format)

    # countdown will be up. if user has reminders on, last reminder should be
    # delivered by this time unless sth went wrong.
    run_dt = dt_obj + dt.timedelta(seconds=10)

    job_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, f"bye {user_id} {cd_name}"))

    sched.add_job(
        goodbye_countdown,
        args=[user_id, cd_name],
        trigger="date",
        id=job_id,
        run_date=run_dt,
        replace_existing=True,
        misfire_grace_time=None,  # delete countdown even if late
    )
    logging.info("Clean up for countdown scheduled successfully.")


async def schedule_all():
    """Recreate all jobs for the apscheduler. Will be used on startup."""
    countdowns = await get_all_countdowns()

    if countdowns:
        for countdown in countdowns:
            name = countdown["name"]
            user_id = countdown["tg_user_id"]
            countdown_dt = countdown["date_time"]
            reminders = countdown["reminders"]
            cd_format = countdown["format"]

            if reminders:
                await schedule_reminders(
                    user_id, name, countdown_dt, cd_format
                )

            await schedule_goodbye_cd(user_id, name, countdown_dt)

        logging.info("Jobs for the apscheduler recreated.")
    else:
        logging.info("No countdowns. No jobs to recreate.")
