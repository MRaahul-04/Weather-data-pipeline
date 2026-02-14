from datetime import datetime
from src.database import get_connection, get_or_create_city
from src.api_client import WeatherAPIClient
from src.validators import validate_weather_data
from src.alerts import evaluate_alerts
from src.logger import logger


class WeatherETLPipeline:
    def __init__(self):
        self.api_client = WeatherAPIClient()

    def start_pipeline_run(self):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO pipeline_runs (run_start, status)
            VALUES (?, ?)
        """, (datetime.utcnow(), "RUNNING"))

        run_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return run_id

    def end_pipeline_run(self, run_id, status, records, error=None):
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE pipeline_runs
            SET run_end = ?, status = ?, records_processed = ?, error_message = ?
            WHERE run_id = ?
        """, (datetime.utcnow(), status, records, error, run_id))

        conn.commit()
        conn.close()

    def load_weather_data(self, city_id, weather):
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO weather_data (
                    city_id, observation_time, temperature_c,
                    humidity, pressure_hpa, wind_speed_mps,
                    weather_condition
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                city_id,
                weather["observation_time"],
                weather["temperature_c"],
                weather["humidity"],
                weather["pressure_hpa"],
                weather["wind_speed_mps"],
                weather["weather_condition"]
            ))
            conn.commit()
        finally:
            conn.close()

    def run(self, cities: list[str]):
        run_id = self.start_pipeline_run()
        records_processed = 0

        try:
            for city_name in cities:
                logger.info(f"Processing city: {city_name}")

                # FK-safe city resolution
                city_id = get_or_create_city(city_name)

                weather = self.api_client.fetch_weather(city_name)

                if validate_weather_data(weather):
                    self.load_weather_data(city_id, weather)
                    evaluate_alerts(city_id, weather)
                    records_processed += 1
                else:
                    logger.warning(f"Validation failed for city: {city_name}")

            self.end_pipeline_run(run_id, "SUCCESS", records_processed)
            logger.info(f"Pipeline run {run_id} completed successfully")

        except Exception as e:
            logger.error(f"Pipeline run {run_id} failed: {e}")
            self.end_pipeline_run(run_id, "FAILED", records_processed, str(e))
            raise
