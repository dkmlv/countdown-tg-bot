import datetime as dt

from dateutil import tz

from utils.get_db_data import get_tz_info


async def convert_dt(user_id: int, countdown_dt: str) -> str:
    """Convert countdown datetime from UTC back to user's timezone.

    This will be used when showing countdown datetime in the Edit Countdown
    menu.

    Parameters
    ----------
    user_id : int
        Telegram user id
    countdown_dt : str
        Countdown date and time in the "%Y-%m-%dT%H:%M:%S%z" format

    """
    countdown_dt_obj = dt.datetime.strptime(
        countdown_dt, "%Y-%m-%dT%H:%M:%S%z"
    )
    users_tz_str = await get_tz_info(user_id)
    # countdown cant be created unless theres tz info available
    # thus users_tz_str should not be None
    assert users_tz_str is not None

    users_tz = tz.gettz(users_tz_str)
    countdown_in_users_tz = countdown_dt_obj.astimezone(users_tz).strftime(
        "%Y-%m-%d %H:%M"
    )

    return countdown_in_users_tz
