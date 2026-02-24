# Run using - [ python -c "from src.reporter import generate_daily_report, generate_daily_csv; print(generate_daily_report()); print(generate_daily_csv()) ]

import csv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
from src.analytics import (
    latest_pipeline_run,
    latest_weather_snapshot,
    alert_summary,
    database_statistics,
    highest_avg_temperature
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REPORT_DIR = PROJECT_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

IST = ZoneInfo("Asia/Kolkata")

def format_ist(dt):
    """
    Convert datetime or datetime string to IST and format for reports.
    """
    if not dt:
        return "N/A"

    # If SQLite returned a string, parse it
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt)
        except ValueError:
            return dt  # fallback: return raw string

    # Ensure UTC timezone
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    ist_time = dt.astimezone(IST)
    return ist_time.strftime("%d %b %Y, %I:%M %p IST")

def generate_daily_report():
    now = datetime.now(timezone.utc)

    pipeline = latest_pipeline_run()
    snapshot = latest_weather_snapshot()
    alerts = alert_summary()
    stats = database_statistics()
    hottest_city, hottest_temp = highest_avg_temperature()

    report = f"""
WEATHER DATA PIPELINE SYSTEM
============================

📊 SYSTEM STATUS
----------------
Status: {pipeline['status'] if pipeline else 'N/A'}
Last Run Start: {format_ist(pipeline['run_start']) if pipeline else 'N/A'}
Last Run End: {format_ist(pipeline['run_end']) if pipeline else 'N/A'}
Records Processed: {pipeline['records'] if pipeline else 'N/A'}
Last Error: {pipeline['error'] or 'None'}

🌤️ CURRENT WEATHER SNAPSHOT
----------------------------
"""

    for s in snapshot:
        report += (
            f"📍 {s['city']}: {s['temperature']}°C, "
            f"{s['humidity']}% humidity, "
            f"{s['condition']}\n"
        )

    report += "\n📅 TODAY'S ALERTS\n-----------------\n"

    if alerts:
        for a in alerts:
            report += (
                f"• {a['type']} alert: {a['city']} "
                f"({a['actual']} > {a['threshold']})\n"
            )
    else:
        report += "• No alerts triggered today\n"

    report += f"""
📊 DATABASE STATISTICS
---------------------
Total Records: {stats['records']}
Cities Tracked: {stats['cities']}
Average Temperature: {stats['avg_temp']} °C

🔥 HOTTEST CITY (LONG-TERM)
--------------------------
City: {hottest_city}
Average Temperature: {hottest_temp} °C

⏰ REPORT GENERATED AT
---------------------
{format_ist(now)}
"""

    report_path = REPORT_DIR / "daily_report.txt"
    report_path.write_text(report.strip(), encoding="utf-8")

    # Generate CSV automatically
    csv_path = generate_daily_csv()

    return report_path, csv_path

def generate_daily_csv():
    snapshot = latest_weather_snapshot()
    csv_path = REPORT_DIR / "daily_report.csv"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["city", "temperature", "humidity", "condition", "time"]
        )
        writer.writeheader()
        writer.writerows(snapshot)

    return csv_path


if __name__ == "__main__":
    generate_daily_report()