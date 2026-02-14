-- database/analytics_queries.sql

-- Q1: Highest average temperature city
SELECT
    c.city_name,
    ROUND(AVG(w.temperature_c), 2) AS avg_temperature
FROM weather_data w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name
ORDER BY avg_temperature DESC
LIMIT 1;

-- Q2: Temperature Trend – Last 30 Days
SELECT
    DATE(observation_time) AS date,
    ROUND(AVG(temperature_c), 2) AS avg_temp
FROM weather_data
WHERE observation_time >= DATE('now', '-30 days')
GROUP BY DATE(observation_time)
ORDER BY date;


-- Q3: Humidity vs Rainfall Correlation (Proxy)
SELECT
    ROUND(AVG(humidity), 2) AS avg_humidity,
    COUNT(*) AS rainy_records
FROM weather_data
WHERE weather_condition LIKE '%rain%';


-- Q4: Extreme Weather by Season
SELECT
    CASE
        WHEN strftime('%m', observation_time) IN ('12','01','02') THEN 'Winter'
        WHEN strftime('%m', observation_time) IN ('03','04','05') THEN 'Summer'
        WHEN strftime('%m', observation_time) IN ('06','07','08','09') THEN 'Monsoon'
        ELSE 'Post-Monsoon'
    END AS season,
    MAX(temperature_c) AS max_temp,
    MIN(temperature_c) AS min_temp
FROM weather_data
GROUP BY season;


-- Q5: Peak Temperature Hours per City
SELECT
    c.city_name,
    strftime('%H', observation_time) AS hour,
    ROUND(AVG(temperature_c), 2) AS avg_temp
FROM weather_data w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name, hour
ORDER BY avg_temp DESC;

-- Q6: KPI Snapshot Queries
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT city_id) AS cities_tracked,
    ROUND(AVG(temperature_c), 2) AS avg_temp_overall
FROM weather_data;

-- If you want to delete the previous pipelines
DELETE FROM pipeline_runs;
DELETE FROM sqlite_sequence WHERE name='pipeline_runs';