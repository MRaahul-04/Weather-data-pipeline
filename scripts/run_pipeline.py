# -------------------------------------------------
# Entry point script to execute the ETL pipeline
# -------------------------------------------------
from src.etl_pipeline import WeatherETLPipeline
from src.database import get_city_map

if __name__ == "__main__":
    # Initialize the ETL pipeline instance
    pipeline = WeatherETLPipeline()

    # Fetch city mapping from database (not directly used here,
    # but kept for future extensibility and validation)
    city_map = get_city_map()

    # List of cities to be processed in this ETL run
    CITIES = [
        "Mumbai",
        "Delhi",
        "Bangalore",
        "Chennai",
        "Kolkata",
        "Hyderabad",
        "Pune",
        "Ahmedabad",
        "Jaipur",
    ]

    # Execute the ETL pipeline for the defined cities
    pipeline.run(CITIES)
    print("✅ ETL Pipeline execution completed")
