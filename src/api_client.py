import os
import time
import certifi
import requests
from dotenv import load_dotenv
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
TIMEOUT = int(os.getenv("API_TIMEOUT", 10))
RETRIES = int(os.getenv("API_RETRIES", 3))

BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

class WeatherAPIClient:
    def __init__(self):
        if not API_KEY:
            raise ValueError("❌ OPENWEATHER_API_KEY not set")

    def fetch_weather(self, city: str) -> dict | None:
        params = {
            "q": city,
            "appid": API_KEY,
            "units": "metric"
        }

        for attempt in range(1, RETRIES + 1):
            try:
                response = requests.get(
                    BASE_URL,
                    params=params,
                    timeout=TIMEOUT,
                    verify=False
                )
                response.raise_for_status()
                data = response.json()

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
                print(f"⚠️ Attempt {attempt} failed for {city}: {e}")
                time.sleep(2)

        print(f"❌ All retries failed for {city}")
        return None
