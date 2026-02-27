import pytest
from src.database import get_connection

@pytest.mark.integration
def test_database_connection():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "cities" in tables
    assert "weather_data" in tables
