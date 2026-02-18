from src.database import get_connection

def highest_avg_temperature():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT c.city_name, ROUND(AVG(w.temperature_c), 2)
        FROM weather_data w
        JOIN cities c ON w.city_id = c.city_id
        GROUP BY c.city_name
        ORDER BY AVG(w.temperature_c) DESC
        LIMIT 1
    """)

    result = cursor.fetchone()
    conn.close()
    return result

def latest_pipeline_run():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT run_start, run_end, status, records_processed, error_message
        FROM pipeline_runs
        ORDER BY run_id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "run_start": row[0],
        "run_end": row[1],
        "status": row[2],
        "records": row[3],
        "error": row[4]
    }


def latest_weather_snapshot():
    conn = get_connection()
    cursor = conn.cursor()

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

    rows = cursor.fetchall()
    conn.close()

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
    conn = get_connection()
    cursor = conn.cursor()

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

    rows = cursor.fetchall()
    conn.close()

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
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total_records,
            COUNT(DISTINCT city_id) AS cities,
            ROUND(AVG(temperature_c), 2) AS avg_temp
        FROM weather_data
    """)

    row = cursor.fetchone()
    conn.close()

    return {
        "records": row[0],
        "cities": row[1],
        "avg_temp": row[2]
    }
