from src.api_client import WeatherAPIClient
import warnings
warnings.filterwarnings("ignore")

client = WeatherAPIClient()

cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata"]

for city in cities:
    data = client.fetch_weather(city)
    print(city, "→", data)

