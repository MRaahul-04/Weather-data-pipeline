import sqlite3
from pathlib import Path

# -------------------------------------------------------------------
# Path resolution for project root and database file location
# -------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "weather_data.db"

def get_connection():
    """
    Create and return a new SQLite connection to the weather database.
    Enables foreign key constraints and sets journal mode to WAL.
    """
    conn = sqlite3.connect(DB_PATH, timeout=30)
    # Enable foreign key support
    conn.execute("PRAGMA foreign_keys = ON")
    # Use Write-Ahead Logging for better concurrency
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def get_city_map():
    """
    Retrieve a dictionary mapping city names to their city IDs.
    Returns:
        dict[str, int]: Mapping from city_name to city_id.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Fetch city_id and city_name pairs from cities table
    cursor.execute("SELECT city_id, city_name FROM cities")
    rows = cursor.fetchall()

    conn.close()

    # Construct and return mapping {city_name: city_id}
    return {city_name: city_id for city_id, city_name in rows}


def get_or_create_city(city_name, country=None, lat=None, lon=None):
    """
    Fetch the city_id for a given city_name, or insert a new city record if not found.
    Args:
        city_name (str): Name of the city.
        country (str, optional): Country code or name.
        lat (float, optional): Latitude coordinate.
        lon (float, optional): Longitude coordinate.
    Returns:
        int: city_id of the existing or newly created city.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Check if city already exists
    cursor.execute(
        "SELECT city_id FROM cities WHERE city_name = ?",
        (city_name,)
    )
    row = cursor.fetchone()

    if row:
        conn.close()
        return row[0]

    # Insert new city record
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
    Fetch all city names from the cities table, ordered alphabetically.
    Returns:
        list[str]: List of city names.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Query all city names ordered by name
    cursor.execute("SELECT city_name FROM cities ORDER BY city_name")
    rows = cursor.fetchall()

    conn.close()

    return [row[0] for row in rows]