"""
backfill_city_geo.py
--------------------------------------------------
Purpose:
    Backfill missing geographic metadata (country, latitude, longitude)
    for cities stored in the database using the OpenWeather API.

When to run:
    - After initial database creation
    - If cities table contains NULL latitude / longitude values
    - During first-time setup or data repair

Behavior:
    - Fetches all cities with missing geo information
    - Calls OpenWeather API for each city
"""

import os
import requests
from src.database import get_connection
from dotenv import load_dotenv
load_dotenv()

GEOCODE_URL = "https://api.openweathermap.org/data/2.5/weather"
API_KEY = os.getenv("OPENWEATHER_API_KEY")
TIMEOUT = int(os.getenv("API_TIMEOUT", 10))
RETRIES = int(os.getenv("API_RETRIES", 3))

if not API_KEY:
    raise RuntimeError("OPENWEATHER_API_KEY is not set")

conn = get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT city_id, city_name
    FROM cities
    WHERE latitude IS NULL OR longitude IS NULL
""")

cities = cursor.fetchall()

if not cities:
    print("✔ No cities require backfilling")
    exit(0)

for city_id, city_name in cities:
    try:
        r = requests.get(
            GEOCODE_URL,
            params={"q": city_name, "limit": 1, "appid": API_KEY},
            timeout=10
        )
        r.raise_for_status()
        data = r.json()

        if not data:
            print(f"⚠ No geo data for {city_name}")
            continue

        country = data[0].get("country")
        lat = data[0].get("lat")
        lon = data[0].get("lon")

        cursor.execute("""
            UPDATE cities
            SET country = ?, latitude = ?, longitude = ?
            WHERE city_id = ?
        """, (country, lat, lon, city_id))

        print(f"✔ Updated {city_name}")

    except Exception as e:
        print(f"❌ Failed for {city_name}: {e}")

conn.commit()
conn.close()

print("✅ City geo backfill completed")