/* ============================================================
   QUERY 1: Hottest City by Average Temperature

   WHY THIS QUERY EXISTS: Identifies consistently hot regions for climate insights and long-term monitoring.
   USED IN: Daily Report, Dashboard KPI
   NOTES: Uses historical average across all available records.
   ============================================================ */
SELECT
    c.city_name,
    ROUND(AVG(w.temperature_c), 2) AS avg_temperature
FROM weather_data w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name
ORDER BY avg_temperature DESC
LIMIT 1;

/* ============================================================
   QUERY 2: Temperature Trend (Last 30 Days)

   WHY THIS QUERY EXISTS:Helps identify short-term climate trends and anomalies.
   USED IN:Trend Analysis, Dashboard Line Chart
   NOTES:Aggregated daily averages over recent data.
   ============================================================ */
SELECT
    DATE(observation_time) AS date,
    ROUND(AVG(temperature_c), 2) AS avg_temp
FROM weather_data
WHERE observation_time >= DATE('now', '-30 days')
GROUP BY DATE(observation_time)
ORDER BY date;


/* ============================================================
   QUERY 3: Humidity vs Rain Conditions

   WHY THIS QUERY EXISTS:Supports correlation analysis between humidity and rain.
   USED IN:Analytical Insights, Report Section
   NOTES:Rain identified using weather condition text.
   ============================================================ */
SELECT
    ROUND(AVG(humidity), 2) AS avg_humidity,
    COUNT(*) AS rainy_records
FROM weather_data
WHERE weather_condition LIKE '%rain%';


/* ============================================================
   QUERY 4: Seasonal Temperature Extremes

   WHY THIS QUERY EXISTS:Enables seasonal comparison and climate pattern analysis.
   USED IN:Analytics Report, Seasonal Insights
   NOTES:Seasons derived from month of observation.
   ============================================================ */
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


/* ============================================================
   QUERY 5: Peak Temperature Hours by City

   WHY THIS QUERY EXISTS:Helps understand daily temperature patterns per city.
   USED IN:Time-Based Analysis, Dashboard Insights
   NOTES:Hour extracted from observation timestamp.
   ============================================================ */
SELECT
    c.city_name,
    strftime('%H', observation_time) AS hour,
    ROUND(AVG(temperature_c), 2) AS avg_temp
FROM weather_data w
JOIN cities c ON w.city_id = c.city_id
GROUP BY c.city_name, hour
ORDER BY avg_temp DESC;

/* ============================================================
   QUERY 6: Database KPI Summary

   WHY THIS QUERY EXISTS:Provides quick system health and data coverage metrics.
   USED IN:Dashboard KPIs, Daily Report Summary
   NOTES:Snapshot metrics calculated at query time.
   ============================================================ */
SELECT
    COUNT(*) AS total_records,
    COUNT(DISTINCT city_id) AS cities_tracked,
    ROUND(AVG(temperature_c), 2) AS avg_temp_overall
FROM weather_data;

/* ============================================================
   If you want to delete the previous pipelines
   ============================================================ */
DELETE FROM pipeline_runs;
DELETE FROM sqlite_sequence WHERE name='pipeline_runs';