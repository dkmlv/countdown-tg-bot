from datetime import datetime as dt
import logging
from typing import Union

from dateutil import tz


async def validate_dt(countdown_dt: str, time_zone: str) -> Union[str, None]:
    """Checks if the provided countdown date and time is valid.

    For the date and time to be valid, it needs to be a future date in %Y-%m-%d
    %H-%M format. Datetime module is used to check if date and time was
    provided in the correct format and to check that it hasn't passed yet.

    The date is additionally first converted to UTC from user's provided time
    zone using the dateutil and datetime modules.

    Parameters
    ----------
    countdown_dt : str
        date and time to validate
    time_zone: str
        user's timezone

    Returns
    -------
    Union[str, None]
        A datetime str (date converted from provided time zone to UTC timezone)
        if the date is valid, else None.
    """

    dt_format = "%Y-%m-%d %H:%M"

    try:
        date_object = dt.strptime(countdown_dt, dt_format)
    except ValueError:
        logging.info("User provided incorrect date and time.")
        return None
    else:
        users_tz = tz.gettz(time_zone)
        utc_zone = tz.gettz("UTC")

        # Make the object timezone aware
        date_object = date_object.replace(tzinfo=users_tz)

        utc_date = date_object.astimezone(utc_zone)

        utc_now = dt.now(utc_zone)

        # if the provided date is in the future and not today
        time_diff = (utc_date - utc_now).seconds
        if utc_date > utc_now and time_diff > 15:
            return utc_date.strftime("%Y-%m-%d %H:%M")
        else:
            return None
