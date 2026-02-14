from datetime import datetime

def validate_weather_data(weather: dict) -> bool:
    if weather is None:
        return False

    if not (-90 <= weather["temperature_c"] <= 60):
        return False

    if not (0 <= weather["humidity"] <= 100):
        return False

    if weather["pressure_hpa"] <= 0:
        return False

    if weather["wind_speed_mps"] < 0:
        return False

    if not isinstance(weather["observation_time"], datetime):
        return False

    return True
