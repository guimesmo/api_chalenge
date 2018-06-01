from urllib.parse import urlencode

import requests

API_KEY = "AIzaSyBgK3qOTtWzaQRtXLnwzvvYv_abXfQm_Ow"


class LocationError(Exception):
    pass


def geolocation_for_address(full_address):
    target_url = 'https://maps.googleapis.com/maps/api/geocode/json?'

    params = {
        "key": API_KEY,
        "address": full_address
    }

    response = requests.get(target_url + urlencode(params))

    if response.status_code == 200:
        data = response.json()
        try:
            return data['results'][0]['geometry']['location']
        except (IndexError, KeyError):
            raise LocationError("Geolocation not found")
    else:
        raise LocationError("Geolocation not found")
