# This script runs the ETL pipeline on a schedule.
import schedule
import time
from src.etl_pipeline import WeatherETLPipeline
from src.database import get_all_city_names
from src.logger import logger

# Scheduled ETL execution job
def job():
    # Retrieve all configured cities from the database
    cities = get_all_city_names()

    # Skip execution if no cities are available
    if not cities:
        logger.warning("No cities found in database. Skipping ETL run.")
        return

    # Trigger the ETL pipeline for all cities
    logger.info(f"Running ETL for {len(cities)} cities")
    WeatherETLPipeline().run(cities)
    logger.info("Scheduled ETL job finished")

# Standalone scheduler execution
if __name__ == "__main__":
    print("⏱️ Scheduler started...")
    logger.info("Scheduler started")

    # Run once at startup
    job()

    # Hourly scheduling
    schedule.every(1).hours.do(job)

    # Keep the scheduler alive
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    # Graceful shutdown on manual interrupt
    except KeyboardInterrupt:
        logger.warning("Scheduler stopped manually")
