# from datetime import datetime
#
# def validate_weather_data(weather: dict) -> bool:
#     if weather is None:
#         return False
#
#     if not (-90 <= weather["temperature_c"] <= 60):
#         return False
#
#     if not (0 <= weather["humidity"] <= 100):
#         return False
#
#     if weather["pressure_hpa"] <= 0:
#         return False
#
#     if weather["wind_speed_mps"] < 0:
#         return False
#
#     if not isinstance(weather["observation_time"], datetime):
#         return False
#
#     return True

def validate_weather_data(weather: dict) -> bool:
    if not isinstance(weather, dict):
        return False

    required_keys = [
        "temperature_c",
        "humidity",
        "pressure_hpa",
        "wind_speed_mps",
        "weather_condition",
        "observation_time",
    ]

    for key in required_keys:
        if key not in weather or weather[key] is None:
            return False

    try:
        temp = float(weather["temperature_c"])
        humidity = int(weather["humidity"])
        pressure = float(weather["pressure_hpa"])
        wind = float(weather["wind_speed_mps"])
    except (ValueError, TypeError):
        return False

    if not (-90 <= temp <= 60):
        return False
    if not (0 <= humidity <= 100):
        return False
    if not (800 <= pressure <= 1100):
        return False
    if wind < 0:
        return False

    return True