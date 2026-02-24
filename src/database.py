import os
import sqlite3
from pathlib import Path
import requests
from src.logger import logger

GEOCODE_URL = "http://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "weather_data.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_city_map():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT city_id, city_name FROM cities")
    rows = cursor.fetchall()

    conn.close()

    return {city_name: city_id for city_id, city_name in rows}


def get_or_create_city(city_name: str) -> int:
    """
    Fetch city_id if exists.
    If not, enrich city metadata using OpenWeather Geocoding API
    and insert safely.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # 1️⃣ Check if city already exists
    cursor.execute(
        "SELECT city_id FROM cities WHERE city_name = ?",
        (city_name,)
    )
    row = cursor.fetchone()

    if row:
        conn.close()
        return row[0]

    # 2️⃣ Fetch geo metadata from OpenWeather
    country = None
    lat = None
    lon = None

    try:
        response = requests.get(
            GEOCODE_URL,
            params={
                "q": city_name,
                "limit": 1,
                "appid": OPENWEATHER_API_KEY
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        if data:
            country = data[0].get("country")
            lat = data[0].get("lat")
            lon = data[0].get("lon")

    except Exception as e:
        logger.warning(f"City geo enrichment failed for {city_name}: {e}")

    # 3️⃣ Insert city safely (with or without geo data)
    cursor.execute(
        """
        INSERT INTO cities (city_name, country, latitude, longitude)
        VALUES (?, ?, ?, ?)
        """,
        (city_name, country, lat, lon)
    )

    city_id = cursor.lastrowid
    conn.commit()
    conn.close()

    logger.info(
        f"City created: {city_name} "
        f"(country={country}, lat={lat}, lon={lon})"
    )

    return city_id

# def get_or_create_city(city_name, country=None, lat=None, lon=None):
#     conn = get_connection()
#     cursor = conn.cursor()
#
#     cursor.execute(
#         "SELECT city_id FROM cities WHERE city_name = ?",
#         (city_name,)
#     )
#     row = cursor.fetchone()
#
#     if row:
#         conn.close()
#         return row[0]
#
#     cursor.execute("""
#         INSERT INTO cities (city_name, country, latitude, longitude)
#         VALUES (?, ?, ?, ?)
#     """, (city_name, country, lat, lon))
#
#     city_id = cursor.lastrowid
#     conn.commit()
#     conn.close()
#     return city_id

def get_all_city_names():
    """
    Fetch all city names from the cities table.
    Returns: list[str]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT city_name FROM cities ORDER BY city_name")
    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]