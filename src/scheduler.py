import schedule
import time
from src.etl_pipeline import WeatherETLPipeline
from src.database import get_all_city_names
from src.logger import logger

def job():
    cities = get_all_city_names()

    if not cities:
        logger.warning("No cities found in database. Skipping ETL run.")
        return

    logger.info(f"Running ETL for {len(cities)} cities")
    WeatherETLPipeline().run(cities)
    logger.info("Scheduled ETL job finished")

if __name__ == "__main__":
    print("⏱️ Scheduler started...")
    logger.info("Scheduler started")

    # Run immediately
    job()

    # Schedule hourly
    schedule.every(1).hours.do(job)

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.warning("Scheduler stopped manually")
