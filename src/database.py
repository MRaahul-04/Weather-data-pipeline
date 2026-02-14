import sqlite3
from pathlib import Path

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


def get_or_create_city(city_name, country=None, lat=None, lon=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT city_id FROM cities WHERE city_name = ?",
        (city_name,)
    )
    row = cursor.fetchone()

    if row:
        conn.close()
        return row[0]

    cursor.execute("""
        INSERT INTO cities (city_name, country, latitude, longitude)
        VALUES (?, ?, ?, ?)
    """, (city_name, country, lat, lon))

    city_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return city_id

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