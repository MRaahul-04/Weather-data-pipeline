# This script orchestrates the full Weather Data Pipeline system lifecycle,
# managing database initialization, data enrichment, ETL pipeline execution,
# scheduling, reporting, and launching the Streamlit dashboard.

import subprocess
import sys
import time
from pathlib import Path
import os

# =================================================
# PATHS & CONSTANTS
# Define key paths and constants used throughout the pipeline
# =================================================
PROJECT_ROOT = Path(__file__).resolve().parent
PYTHON = sys.executable

SCRIPTS_DIR = PROJECT_ROOT / "scripts"
SRC_DIR = PROJECT_ROOT / "src"
DB_PATH = PROJECT_ROOT / "database" / "weather_data.db"

STREAMLIT_PORT = "8501"
background_processes = []

# =================================================
# CLI HELPERS
# Helper functions for printing formatted CLI output
# =================================================
def banner(title):
    """Prints formatted CLI section headers."""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def step(msg):
    """Prints step-in-progress messages."""
    print(f"▶ {msg}")
    sys.stdout.flush()


def done(msg):
    """Prints successful completion messages."""
    print(f"✔ {msg}")
    sys.stdout.flush()


def info(msg):
    """Prints informational messages."""
    print(f"ℹ {msg}")
    sys.stdout.flush()


# =================================================
# PROCESS HELPERS
# Functions to check data status and manage subprocesses
# =================================================
def city_geo_missing():
    """
    Checks if city geo metadata is incomplete.
    Returns True if any city is missing country, latitude, or longitude info.
    """
    import sqlite3

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        SELECT COUNT(*)
        FROM cities
        WHERE country IS NULL
           OR latitude IS NULL
           OR longitude IS NULL
    """)

    missing = cur.fetchone()[0]
    conn.close()
    return missing > 0

def api_key_available():
    """Checks if the OPENWEATHER_API_KEY environment variable is set."""
    return bool(os.getenv("OPENWEATHER_API_KEY"))

def start_background(cmd, label):
    """
    Launches long-running background services as subprocesses.
    Args:
        cmd: List of command arguments to run.
        label: Descriptive label for the service.
    Returns:
        The subprocess.Popen object for the started process.
    """
    step(label)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == "nt" else 0,
    )
    background_processes.append(proc)
    done(f"{label} started")
    return proc


def run_once(cmd, label):
    """
    Executes one-time scripts synchronously, displaying progress.
    Args:
        cmd: List of command arguments to run.
        label: Descriptive label for the task.
    """
    step(label)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)

    subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        env=env,
        stdout=sys.stdout,
        stderr=sys.stderr,
        check=True,
    )
    done(label + " completed")


def shutdown():
    """
    Gracefully terminates all background services and exits the program.
    """

    print("=" * 60)
    print("🔚 DASHBOARD STOPPED")
    print("=" * 60)

    print("\n" + "=" * 60)
    print("🛑 SHUTTING DOWN WEATHER DATA PIPELINE SYSTEM")
    print("=" * 60 + "\n")

    for proc in background_processes:
        try:
            proc.terminate()
        except Exception:
            pass

    time.sleep(1)

    for proc in background_processes:
        if proc.poll() is None:
            proc.kill()

    print("✔ All background services stopped")
    print("✔ System stopped safely.\n")

    sys.exit(0)

# =================================================
# MAIN ORCHESTRATION
# Coordinates the full pipeline run and dashboard lifecycle
# =================================================
if __name__ == "__main__":
    try:
        banner("🚀 WEATHER DATA PIPELINE SYSTEM STARTING")

        # -----------------------------
        # DATABASE CHECK
        # Validate presence of database or initialize if missing
        # -----------------------------
        print("▶ 🗄 DATABASE"
              "\n------------------------")
        if DB_PATH.exists():
            done("Database already exists")
        else:
            run_once(
                [PYTHON, SCRIPTS_DIR / "init_db.py"],
                "Initializing database",
            )

        # -----------------------------
        # CITY GEO ENRICHMENT (SAFE)
        # Determine if geo enrichment is needed and if API key is available
        # -----------------------------
        print("\n🌍 CITY GEO ENRICHMENT"
              "\n------------------------")

        if city_geo_missing():
            if api_key_available():
                run_once(
                    [PYTHON, SCRIPTS_DIR / "backfill_city_geo.py"],
                    "Enriching city geo metadata",
                )
            else:
                info("City geo data missing but OPENWEATHER_API_KEY not set")
                info("Skipping geo enrichment (run backfill_city_geo.py later)")
        else:
            done("All city geo metadata already present")

        # -----------------------------
        # ETL PIPELINE
        # Run the initial ETL pipeline to populate weather data
        # -----------------------------
        print("\n🔄 ETL PIPELINE"
              "\n------------------------")
        run_once(
            [PYTHON, SCRIPTS_DIR / "run_pipeline.py"],
            "Initial ETL pipeline run",
        )

        # -----------------------------
        # SCHEDULER
        # Start the scheduler service to automate periodic data updates
        # -----------------------------
        print("\n⏱ SCHEDULER"
              "\n------------------------")
        start_background(
            [PYTHON, SRC_DIR / "scheduler.py"],
            "Weather data scheduler",
        )

        # -----------------------------
        # REPORTING
        # Generate daily reports based on collected data
        # -----------------------------
        print("\n📄 REPORTING"
              "\n------------------------")
        run_once(
            [PYTHON, SRC_DIR / "reporter.py"],
            "Daily report generation",
        )

        # -----------------------------
        # DASHBOARD
        # Launch the Streamlit dashboard for interactive data visualization
        # -----------------------------
        banner("🌐 STREAMLIT DASHBOARD")
        info("🔄Launching Streamlit dashboard")
        info("For Windows:")
        info("Via Git Bash - Run: \"python run_app.py\" & use Ctrl + C to stop safely")
        info("via Terminal/Run - Run: \"python stop_app.py\" to stop safely")

        subprocess.run(
            [
                PYTHON,
                "-m",
                "streamlit",
                "run",
                str(SRC_DIR / "dashboard.py"),
                "--server.port", STREAMLIT_PORT,
                "--server.address", "localhost",
            ],
            cwd=PROJECT_ROOT,
        )

        # -----------------------------
        # POST-DASHBOARD
        # Prompt user to shut down background services after dashboard exit
        # -----------------------------
        banner("🔚 DASHBOARD STOPPED")

        choice = input(
            "Do you want to stop all background services now? (y/n): "
        ).strip().lower()

        if choice == "y":
            shutdown()
        else:
            info("Background services are still running")
            info("To stop them later, run: python stop_app.py")
            sys.exit(0)

    except KeyboardInterrupt:
        shutdown()