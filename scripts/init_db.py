import sqlite3
from pathlib import Path

# Resolve project root safely (works on Windows / macOS / Linux)
PROJECT_ROOT = Path(__file__).resolve().parent.parent

DB_PATH = PROJECT_ROOT / "database" / "weather_data.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"

def init_database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        cursor.executescript(f.read())

    conn.commit()
    conn.close()
    print("✅ Database initialized successfully")

if __name__ == "__main__":
    init_database()
