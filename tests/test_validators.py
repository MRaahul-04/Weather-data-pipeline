# Unit tests for weather data validation logic

import pytest
from src.validators import validate_weather_data

# Mark the following tests as unit tests
@pytest.mark.unit
# Test that valid weather data passes validation
def test_weather_validation_success():
    sample = {
        "temperature_c": 25.0,
        "humidity": 60,
        "pressure_hpa": 1012,
        "wind_speed_mps": 3.5,
        "weather_condition": "clear sky",
        "observation_time": "2026-02-18T10:00:00"
    }
    assert validate_weather_data(sample) is True

# Mark the following tests as unit tests
@pytest.mark.unit
# Test that invalid weather data fails validation
def test_weather_validation_failure():
    bad_sample = {
        "temperature_c": None,
        "humidity": -5
    }
    assert validate_weather_data(bad_sample) is False