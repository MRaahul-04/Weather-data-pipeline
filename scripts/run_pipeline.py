from src.etl_pipeline import WeatherETLPipeline
from src.database import get_city_map

if __name__ == "__main__":
    pipeline = WeatherETLPipeline()

    city_map = get_city_map()
    if not city_map:
        raise RuntimeError("❌ No cities found in database")

    pipeline.run(city_map)
    print("✅ ETL Pipeline execution completed")
