from geolocation import LocationError
from models import Location
import pytest


def test_location_latlong_gettering():
    location = Location(city_name="campinas", uf="sp")
    location.load_lat_lon()
    assert pytest.approx(location.lat, 0.01) == -22.89
    assert pytest.approx(location.lon, 0.01) == -47.10


def test_location_invalid_raises_error():
    location = Location(city_name="a test not a city", uf="sp")
    with pytest.raises(LocationError) as execinfo:
        location.load_lat_lon()
    assert "Geolocation not found" in str(execinfo.value)
