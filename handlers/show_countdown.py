from utils.calculate_diff import calculate_diff
from utils.send_message import send_message


async def send_countdown_details(
    user_id: int, cd_name: str, date_time: str, cd_format: int
):
    """Send how much time is left till the countdown is up.

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

    time_diff = calculate_diff(date_time)

    # didnt want to import math to round up the number
    # basically the idea is to have one "═" for two characters and an extra "═"
    # at the end
    text_divider = "═" * (len(cd_name) // 2 + (len(cd_name) % 2 > 0) + 1)

    text = f"<b>{cd_name}</b>\n{text_divider}\n"

    if cd_format == 1:
        text += f"{time_diff} left"
    else:
        text += "<i>Time left:</i>\n"
        time_diff_list = time_diff.split(", ")

        # last item may be like -> 5 minutes and 6 seconds
        if "and" in time_diff_list[-1]:
            time_diff_list[-1:] = time_diff_list[-1].split(" and ")

        for item in time_diff_list:
            text += f"{item}\n"

    await send_message(user_id, text)
