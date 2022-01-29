import datetime as dt

from humanize.time import precisedelta


def calculate_diff(date_time: str) -> str:
    """Calculate the time difference between specified date and now.

    `precisedelta` from the `humanize` package is used to get a precise
    representation of a timedelta object. 1 year is equivalent to 365 days and
    1 month is equivalent to 30.5 days.

    Parameters
    ----------
    date_time : str
        datetime string (with time zone) in the '%Y-%m-%dT%H:%M:%S%z' format

    Returns
    -------
    str
        difference between specified date and now as a string
    """

    dt_format = "%Y-%m-%dT%H:%M:%S%z"
    dt_obj = dt.datetime.strptime(date_time, dt_format)
    now = dt.datetime.now(dt.timezone.utc)

    difference = dt_obj - now

    # if its very close to being a day, show it as a day
    # instead of '4 days 23 hours 59 minutes 59.99 seconds' show '5 days'
    if difference.seconds >= 86390 and difference.seconds <= 86400:
        return precisedelta(difference, minimum_unit="days", format="%0.f")
    else:
        return precisedelta(difference, format="%0.f")
