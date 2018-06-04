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
        "appid": APP_ID,
        "cnt": 8
    }

    target_url = forecast_url + urlencode(params)

    result = requests.get(target_url)
    if result.status_code == 200:
        return result.json()
    else:
        raise LocationException("Falha na conexão")


class Forecast:
    _hourly_forecast = None

    def __init__(self, lat, lon, forecast_dict=None):
        """
        Forecast interface to send next days forecasts
        :param lat: float. Set None if has the forecast dict
        :param lon: float. Set None if has the forecast dict
        :param forecast_dict: the full payload. For tests or cache
        """
        if not forecast_dict:
            forecast_dict = get_forecast(lat, lon)
        self.forecast_dict = forecast_dict

    @property
    def hourly_forecast(self):
        if not self._hourly_forecast:
            self._hourly_forecast = self.load_hourly_forecast()
        return self._hourly_forecast

    def load_hourly_forecast(self):
        forecast = {}
        for item in self.forecast_dict['list']:
            forecast[item['dt']] = item['weather'][0]['main'].lower()
        return forecast

    def for_timestamp(self, timestamp):
        forecast = self.hourly_forecast
        ts = [k for k in forecast.keys() if k < timestamp]
        if ts:
            return forecast[ts[-1]]
