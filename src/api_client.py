"""
This module handles communication with the OpenWeather API and implements retry logic.
"""
import os
import time
import requests
from dotenv import load_dotenv
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# Load environment variables from .env
load_dotenv()

# Read OpenWeather API key from environment variables
API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Fail fast if the API key is missing
if not API_KEY:
    raise RuntimeError(
        "OPENWEATHER_API_KEY is missing.\n"
        "Set it using:\n"
        "  export OPENWEATHER_API_KEY=your_key   (Git Bash)\n"
        "  setx OPENWEATHER_API_KEY your_key     (PowerShell)"
    )

# Timeout for API requests (seconds) and number of retries
TIMEOUT = int(os.getenv("API_TIMEOUT", 10))
RETRIES = int(os.getenv("API_RETRIES", 3))

# OpenWeather endpoint used for current weather data
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# Client for interacting with the OpenWeather API, with retry logic.
class WeatherAPIClient:
    def __init__(self):
        # Repeat API key validation for safety
        if not API_KEY:
            raise ValueError("❌ OPENWEATHER_API_KEY not set")

    """Fetch weather data for a city from the OpenWeather API.

    Returns a normalized dictionary with weather info, or None if all retries fail.
    """
    def fetch_weather(self, city: str) -> dict | None:
        # Request parameters for OpenWeather API
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        # Retry the request up to RETRIES times
        for attempt in range(1, RETRIES + 1):
            try:
                # Make HTTP GET request to the OpenWeather API
                response = requests.get(
                    BASE_URL,
                    params=params,
                    timeout=TIMEOUT,
                    verify=False
                )
                response.raise_for_status()
                data = response.json()

                # Return normalized weather data structure
                return {
                    "city": city,
                    "observation_time": datetime.utcnow(),
                    "temperature_c": data["main"]["temp"],
                    "humidity": data["main"]["humidity"],
                    "pressure_hpa": data["main"]["pressure"],
                    "wind_speed_mps": data["wind"]["speed"],
                    "weather_condition": data["weather"][0]["description"]
                }

            except requests.RequestException as e:
                # Handle failed attempt and retry after delay
                print(f"⚠️ Attempt {attempt} failed for {city}: {e}")
                time.sleep(2)

        print(f"❌ All retries failed for {city}")
        return None
