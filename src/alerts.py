# This module evaluates weather thresholds and stores alerts in the database.

from datetime import datetime
from src.database import get_connection

# Threshold for high temperature alerts (in degrees Celsius)
TEMP_THRESHOLD = 30.0
# Threshold for high humidity alerts (in percentage)
HUMIDITY_THRESHOLD = 75

def evaluate_alerts(city_id: int, weather: dict):
    """
    Evaluate weather data against predefined thresholds and store alerts in the database.
    Takes a city identifier and a weather dictionary as input.
    Inserts alerts if temperature or humidity exceed their respective thresholds.
    """
    # Collect triggered alerts
    alerts = []

    # Check if temperature exceeds the threshold
    if weather["temperature_c"] > TEMP_THRESHOLD:
        alerts.append((
            "HIGH_TEMPERATURE",
            f"Temperature {weather['temperature_c']}°C exceeds {TEMP_THRESHOLD}°C",
            TEMP_THRESHOLD,
            weather["temperature_c"]
        ))

    # Check if humidity exceeds the threshold
    if weather["humidity"] > HUMIDITY_THRESHOLD:
        alerts.append((
            "HIGH_HUMIDITY",
            f"Humidity {weather['humidity']}% exceeds {HUMIDITY_THRESHOLD}%",
            HUMIDITY_THRESHOLD,
            weather["humidity"]
        ))

    # Persist alerts only if any thresholds are breached
    if not alerts:
        return

    conn = get_connection()
    cursor = conn.cursor()

    # Store each triggered alert individually
    for alert_type, message, threshold, actual in alerts:
        cursor.execute("""
            INSERT INTO alerts (
                city_id, alert_type, alert_message,
                threshold_value, actual_value, triggered_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            city_id, alert_type, message,
            threshold, actual, datetime.utcnow()
        ))

    conn.commit()
    conn.close()
