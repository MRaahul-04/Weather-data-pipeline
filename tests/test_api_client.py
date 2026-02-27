import pytest
from src.api_client import WeatherAPIClient

@pytest.mark.unit
def test_api_client_initialization():
    client = WeatherAPIClient()
    assert client is not None