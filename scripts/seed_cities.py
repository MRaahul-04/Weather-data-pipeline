from src.database import get_or_create_city

CITIES = [
    "Mumbai",
    "Delhi",
    "Bangalore",
    "Chennai",
    "Kolkata",
    "Hyderabad",
    "Pune",
    "Ahmedabad",
    "Jaipur"
]

if __name__ == "__main__":
    for city in CITIES:
        get_or_create_city(city)

    print("✅ Cities seeded successfully")
