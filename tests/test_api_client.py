# Unit tests for the Weather API client

# Importing the pytest testing framework
import pytest
# Importing the WeatherAPIClient class to be tested
from src.api_client import WeatherAPIClient

# Marking the test as a unit test
@pytest.mark.unit
# Test to verify successful instantiation of the WeatherAPIClient
def test_api_client_initialization():
    client = WeatherAPIClient()
    assert client is not None