from typing import Union

from geopy.geocoders import Nominatim


def get_coordinates(address: str) -> Union[dict, None]:
    """Get coordinates (longitude and latitude) for a given address.

    Parameters
    ----------
    address : str
        The address provided by the user

    Returns
    -------
    Union[dict, None]
        dict with longitude and latitude values if location is valid, else None
    """

    geolocator = Nominatim(user_agent="countdownTgBot")
    location = geolocator.geocode(address)

    if location:
        coordinates = {
            "longitude": location.longitude,  # type: ignore
            "latitude": location.latitude,  # type: ignore
        }
        return coordinates
    else:
        return None
