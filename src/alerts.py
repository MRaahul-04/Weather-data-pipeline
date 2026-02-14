from datetime import datetime
from src.database import get_connection

TEMP_THRESHOLD = 30.0
HUMIDITY_THRESHOLD = 75

def evaluate_alerts(city_id: int, weather: dict):
    alerts = []

    if weather["temperature_c"] > TEMP_THRESHOLD:
        alerts.append((
            "HIGH_TEMPERATURE",
            f"Temperature {weather['temperature_c']}°C exceeds {TEMP_THRESHOLD}°C",
            TEMP_THRESHOLD,
            weather["temperature_c"]
        ))

    if weather["humidity"] > HUMIDITY_THRESHOLD:
        alerts.append((
            "HIGH_HUMIDITY",
            f"Humidity {weather['humidity']}% exceeds {HUMIDITY_THRESHOLD}%",
            HUMIDITY_THRESHOLD,
            weather["humidity"]
        ))

    if not alerts:
        return

    conn = get_connection()
    cursor = conn.cursor()

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
