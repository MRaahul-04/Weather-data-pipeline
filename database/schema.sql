PRAGMA foreign_keys = ON;

-- Cities master table
CREATE TABLE IF NOT EXISTS cities (
    city_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_name TEXT NOT NULL,
    country TEXT,
    latitude REAL,
    longitude REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_name, country)
);

-- Weather fact table
CREATE TABLE IF NOT EXISTS weather_data (
    record_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER NOT NULL,
    observation_time TIMESTAMP NOT NULL,
    temperature_c REAL,
    humidity INTEGER,
    pressure_hpa REAL,
    wind_speed_mps REAL,
    weather_condition TEXT,
    data_source TEXT DEFAULT 'OpenWeatherMap',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);

-- Pipeline execution monitoring
CREATE TABLE IF NOT EXISTS pipeline_runs (
    run_id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_start TIMESTAMP,
    run_end TIMESTAMP,
    status TEXT,
    records_processed INTEGER,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Alerts table
CREATE TABLE IF NOT EXISTS alerts (
    alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
    city_id INTEGER,
    alert_type TEXT,
    alert_message TEXT,
    threshold_value REAL,
    actual_value REAL,
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved INTEGER DEFAULT 0,
    FOREIGN KEY (city_id) REFERENCES cities(city_id)
);
