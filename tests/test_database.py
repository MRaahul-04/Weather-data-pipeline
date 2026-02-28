# Integration tests for database connectivity and schema validation.

# Using pytest testing framework
import pytest
# Importing database access function for tests
from src.database import get_connection

# Marking this test as an integration test
@pytest.mark.integration
# Test to verify database connection and presence of required tables
def test_database_connection():
    # Opening a database connection
    conn = get_connection()
    cursor = conn.cursor()
    # Querying SQLite system tables for table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # Collecting table names from query results
    tables = [row[0] for row in cursor.fetchall()]
    # Closing the database connection
    conn.close()

    assert "cities" in tables
    assert "weather_data" in tables
