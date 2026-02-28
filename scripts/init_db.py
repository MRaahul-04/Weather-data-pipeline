"""
init_db.py
--------------------------------------------------
Purpose:
    Initialize the SQLite database for the Weather Data Pipeline system.

When to run:
    - During first-time project setup
    - When resetting the database
    - Automatically triggered via run_app.py if database is missing
"""

# =================================================
# STANDARD LIBRARY IMPORTS
# =================================================
import sqlite3
from pathlib import Path

# =================================================
# PROJECT PATH RESOLUTION
# =================================================
# Resolve project root safely (cross-platform)
# scripts/init_db.py → project_root/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Database file path
DB_PATH = PROJECT_ROOT / "database" / "weather_data.db"

# SQL schema file path
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

# =================================================
# DATABASE INITIALIZATION FUNCTION
# =================================================
def init_database():
    """
    Initialize the SQLite database using the schema.sql file.

    Steps:
        1. Ensure database directory exists
        2. Connect to SQLite database (creates file if missing)
        3. Execute SQL schema script
        4. Commit changes and close connection

    Behavior:
        - Existing tables are preserved (handled by IF NOT EXISTS in schema)
        - Safe to run multiple times
    """

    # Create database directory if it does not exist
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Establish SQLite connection
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Load and execute schema SQL
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    # Persist changes and release resources
    conn.commit()
    conn.close()

    print("✅ Database initialized successfully")

# =================================================
# SCRIPT ENTRY POINT
# =================================================
if __name__ == "__main__":
    init_database()