import re
from typing import Union

from utils.get_db_data import get_countdown_names


async def check_countdown_name(user_id: int, cd_name: str) -> Union[str, None]:
    """Check that countdown name is valid.

    Parameters
    ----------
    user_id : int
        Telegram user id
    cd_name : str
        Countdown name provided by the user

    Returns
    -------
    Union[str, None]
        If countdown name is invalid -> str (message to send back to the user)
        Else (valid countdown name)-> None
    """

    countdown_names = await get_countdown_names(user_id)

    if countdown_names and cd_name in countdown_names:
        text = "You already have a countdown with this name. Try another name."
    elif len(cd_name) > 40:
        text = (
            "Sorry, your countdown name cannot be longer than 40 characters. "
            "Please type another name."
        )
    elif re.match(r"^[\w\s]+$", cd_name):
        text = None
    else:
        text = (
            "Sorry, you can't have special symbols in the countdown name. "
            "Please type the countdown name again."
        )

    return text
