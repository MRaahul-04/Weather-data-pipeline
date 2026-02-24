from src.etl_pipeline import WeatherETLPipeline
from src.database import get_city_map

if __name__ == "__main__":
    pipeline = WeatherETLPipeline()

    city_map = get_city_map()
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

    pipeline.run(CITIES)
    print("✅ ETL Pipeline execution completed")
