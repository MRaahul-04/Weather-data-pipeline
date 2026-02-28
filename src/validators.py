# This module validates incoming weather data before storage.

def validate_weather_data(weather: dict) -> bool:
    """Validate the structure and values of weather data dictionary.

    Returns True if all required fields are present and valid, else False.
    """
    # Ensure the input is a dictionary
    if not isinstance(weather, dict):
        return False

    # Define required keys to be present in the weather data
    required_keys = [
        "temperature_c",
        "humidity",
        "pressure_hpa",
        "wind_speed_mps",
        "weather_condition",
        "observation_time",
    ]

    # Check for any missing or None values in required fields
    for key in required_keys:
        if key not in weather or weather[key] is None:
            return False

    # Attempt to cast fields to expected types to validate format
    try:
        temp = float(weather["temperature_c"])
        humidity = int(weather["humidity"])
        pressure = float(weather["pressure_hpa"])
        wind = float(weather["wind_speed_mps"])
    except (ValueError, TypeError):
        return False

    # Validate temperature range in Celsius
    if not (-90 <= temp <= 60):
        return False
    # Validate humidity percentage range
    if not (0 <= humidity <= 100):
        return False
    # Validate atmospheric pressure range in hPa
    if not (800 <= pressure <= 1100):
        return False
    # Validate wind speed is non-negative
    if wind < 0:
        return False

    return True