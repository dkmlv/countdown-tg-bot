"""Convert date and time objects to UTC."""

from datetime import datetime as dt
from dateutil import tz


async def convert_date(date: str, time_zone: str) -> dt:
    """Convert date from given timezone to UTC.

    Parameters
    ----------
    date : str
        the date that needs to be converted to utc
    time_zone : str
        timezone information to make the datetime object timezone aware

    Returns
    -------
    dt
        datetime object with UTC timezone
    """

    from_zone = tz.gettz(time_zone)
    to_zone = tz.gettz("UTC")

    provided_date = dt.strptime(date, "%Y-%m-%d")
    
    # Make the object timezone aware
    provided_date = provided_date.replace(tzinfo=from_zone)

    utc_date = provided_date.astimezone(to_zone)

    return utc_date
