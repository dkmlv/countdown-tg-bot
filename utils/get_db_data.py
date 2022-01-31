"""Basic select queries."""

from typing import Union

from loader import supabase


async def get_tz_info(user_id: int) -> Union[str, None]:
    """Get user's time zone information from the db.

    Parameters
    ----------
    user_id : int
        Telegram user id

    Returns
    -------
    Union[str, None]
        str if time zone informaton is found, None otherwise.
    """

    tz_info = (
        supabase.table("Accounts")
        .select("time_zone")
        .eq("tg_user_id", user_id)
        .execute()
    )

    try:
        # tz_info[0] -> list containing the results of the query
        # tz-info[0] -> [{'time_zone': 'Asia/Tashkent'}]
        assert len(tz_info[0]) > 0
    except AssertionError:
        return None
    else:
        return tz_info[0][0]["time_zone"]


async def get_countdown_names(user_id: int) -> Union[list, None]:
    """Get user's countdown names from the db.

    Parameters
    ----------
    user_id : int
        Telegram user id

    Returns
    -------
    Union[list, None]
        list if at least one countdown is found, None otherwise.
    """

    data = (
        supabase.table("Countdowns")
        .select("name")
        .eq("tg_user_id", user_id)
        .execute()
    )

    try:
        # data[0] -> [{'name': 'end of the world'}, {'name': 'hello there'}]
        assert len(data[0]) > 0
    except AssertionError:
        return None
    else:
        return [countdown["name"] for countdown in data[0]]


async def get_countdown_details(user_id: int, name: str) -> Union[dict, None]:
    """Get specific countdown's details from the db.

    Parameters
    ----------
    user_id : int
        Telegram user id
    name : str
        Countdown name

    Returns
    -------
    Union[dict, None]
        Countdown details as a dictionary if countdown is found, None otherwise
    """

    data = (
        supabase.table("Countdowns")
        .select("*")
        .eq("tg_user_id", user_id)
        .eq("name", name)
        .execute()
    )

    try:
        # data[0] -> [{'date_time': '2022-01-29T10:00:00+00:00', 'format': 2}]
        assert len(data[0]) > 0
    except AssertionError:
        return None
    else:
        return data[0][0]


async def get_all_countdowns() -> Union[list, None]:
    """Get a list of all countdown.

    Returns
    -------
    Union[list, None]
        A list of all countdowns if at least one is found, else None
    """

    data = supabase.table("Countdowns").select("*").execute()

    try:
        assert len(data[0]) > 0
    except AssertionError:
        return None
    else:
        return data[0]
