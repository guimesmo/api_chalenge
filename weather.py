from urllib.parse import urlencode

import requests

BASE_URL = "http://api.openweathermap.org/data/2.5"
APP_ID = "46587ea4da2c2e17c21a4fdabb6efcda"


class LocationException(Exception):
    pass


def get_forecast(lat, lon):
    forecast_url = BASE_URL + "/forecast?"

    params = {
        "lat": lat,
        "lon": lon,
        "mode": "json",
        "appid": APP_ID
    }

    target_url = forecast_url + urlencode(params)

    result = requests.get(target_url)
    if result.status_code == 200:
        return result.json()
    else:
        raise LocationException("Falha na conexão")


class Forecast:
    def __init__(self, lat, lon):
        forecast_dict = get_forecast(lat, lon)
        self.todays_forecast = forecast_dict['list'][0]['weather'][0]['main'].lower()
        self.next_day_forecast = forecast_dict['list'][1]['weather'][0]['main'].lower()
