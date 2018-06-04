import json

from weather import Forecast


def test_weather_forecast_with_clouds_sky():
    with open("tests/data/forecast.json") as opened_file:
        forecast_dict = json.loads(opened_file.read())
    forecast = Forecast(None, None, forecast_dict)
    forecast_dict = forecast.load_hourly_forecast()
    assert forecast_dict[1528092000] == "clouds"


def test_weather_forecast_for_hour():
    with open("tests/data/forecast.json") as opened_file:
        forecast_dict = json.loads(opened_file.read())
    forecast = Forecast(None, None, forecast_dict)
    assert forecast.for_timestamp(1528103800) == "rain"

