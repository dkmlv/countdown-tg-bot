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
