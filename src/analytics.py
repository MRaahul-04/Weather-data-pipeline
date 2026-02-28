# This module provides read-only analytical queries for reporting and dashboards.

# Import database connection utility
from src.database import get_connection

def highest_avg_temperature():
    """
    Returns the city with the highest average temperature.
    Used in temperature analytics reports and dashboards.
    """
    # Establish a read-only database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Execute query to find city with highest average temperature
    cursor.execute("""
        SELECT c.city_name, ROUND(AVG(w.temperature_c), 2)
        FROM weather_data w
        JOIN cities c ON w.city_id = c.city_id
        GROUP BY c.city_name
        ORDER BY AVG(w.temperature_c) DESC
        LIMIT 1
    """)

    # Fetch the single result row (city name and avg temperature)
    result = cursor.fetchone()
    conn.close()
    # Return tuple: (city_name, average_temperature)
    return result

def latest_pipeline_run():
    """
    Returns details of the most recent pipeline run.
    Used in ETL monitoring dashboards and reports.
    """
    # Establish a read-only database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Execute query to retrieve latest pipeline run details
    cursor.execute("""
        SELECT run_start, run_end, status, records_processed, error_message
        FROM pipeline_runs
        ORDER BY run_id DESC
        LIMIT 1
    """)

    # Fetch the latest pipeline run row
    row = cursor.fetchone()
    conn.close()

    if not row:
        # Return None if no pipeline runs exist
        return None

    # Return dictionary with run details keyed by descriptive names
    return {
        "run_start": row[0],
        "run_end": row[1],
        "status": row[2],
        "records": row[3],
        "error": row[4]
    }


def latest_weather_snapshot():
    """
    Returns the latest weather data snapshot for all cities.
    Used in real-time weather dashboards and analytics.
    """
    # Establish a read-only database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Execute query to get most recent weather observation per city
    cursor.execute("""
        SELECT
            c.city_name,
            w.temperature_c,
            w.humidity,
            w.weather_condition,
            w.observation_time
        FROM weather_data w
        JOIN cities c ON w.city_id = c.city_id
        WHERE w.observation_time = (
            SELECT MAX(w2.observation_time)
            FROM weather_data w2
            WHERE w2.city_id = w.city_id
        )
        ORDER BY c.city_name
    """)

    # Fetch all rows for latest weather snapshots
    rows = cursor.fetchall()
    conn.close()

    # Return list of dictionaries with weather details by city
    return [
        {
            "city": r[0],
            "temperature": r[1],
            "humidity": r[2],
            "condition": r[3],
            "time": r[4]
        }
        for r in rows
    ]

def alert_summary():
    """
    Returns a summary of alerts triggered today.
    Used in alert monitoring dashboards and reports.
    """
    # Establish a read-only database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Execute query to retrieve alerts triggered today with city info
    cursor.execute("""
        SELECT
            c.city_name,
            a.alert_type,
            a.actual_value,
            a.threshold_value,
            a.triggered_at
        FROM alerts a
        JOIN cities c ON a.city_id = c.city_id
        WHERE DATE(a.triggered_at) = DATE('now')
        ORDER BY a.triggered_at DESC
    """)

    # Fetch all alert rows triggered today
    rows = cursor.fetchall()
    conn.close()

    # Return list of dictionaries summarizing alert details
    return [
        {
            "city": r[0],
            "type": r[1],
            "actual": r[2],
            "threshold": r[3],
            "time": r[4]
        }
        for r in rows
    ]

def database_statistics():
    """
    Returns overall statistics about the weather data in the database.
    Used in system health and data quality dashboards.
    """
    # Establish a read-only database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Execute query to count records, distinct cities, and average temperature
    cursor.execute("""
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT city_id) AS cities,
            ROUND(AVG(temperature_c), 2) AS avg_temp
        FROM weather_data
    """)

    # Fetch single row with database statistics
    row = cursor.fetchone()
    conn.close()

    # Return dictionary with total records, city count, and average temperature
    return {
        "records": row[0],
        "cities": row[1],
        "avg_temp": row[2]
    }
