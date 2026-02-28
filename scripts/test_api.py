# -------------------------------------------------
# Simple API test script for WeatherAPIClient
# Used to manually verify API connectivity and data fetch
# -------------------------------------------------

from src.api_client import WeatherAPIClient
import warnings
warnings.filterwarnings("ignore")

# Initialize the API client
client = WeatherAPIClient()

# List of cities to test API responses
cities = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Chennai",
    "Kolkata",
    "Hyderabad",
    "Pune",
    "Ahmedabad",
    "Jaipur"
]

# Fetch and print weather data for each city
for city in cities:
    data = client.fetch_weather(city)
    print(city, "→", data)