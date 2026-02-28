import subprocess
import sys
import time
from pathlib import Path
import os

# =================================================
# PATHS & CONSTANTS
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
# =================================================
def banner(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70 + "\n")


def step(msg):
    print(f"▶ {msg}")
    sys.stdout.flush()


def done(msg):
    print(f"✔ {msg}")
    sys.stdout.flush()


def info(msg):
    print(f"ℹ {msg}")
    sys.stdout.flush()


# =================================================
# PROCESS HELPERS
# =================================================
def city_geo_missing():
    """
    Returns True if any city is missing geo metadata.
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
    return bool(os.getenv("OPENWEATHER_API_KEY"))

def start_background(cmd, label):
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

    print("=" * 60)
    print("🔚 DASHBOARD STOPPED")
    print("=" * 60)

    sys.exit(0)

# =================================================
# MAIN ORCHESTRATION
# =================================================
if __name__ == "__main__":
    try:
        banner("🚀 WEATHER DATA PIPELINE SYSTEM STARTING")

        # -----------------------------
        # DATABASE CHECK
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
        # -----------------------------
        print("\n🔄 ETL PIPELINE"
              "\n------------------------")
        run_once(
            [PYTHON, SCRIPTS_DIR / "run_pipeline.py"],
            "Initial ETL pipeline run",
        )

        # -----------------------------
        # SCHEDULER
        # -----------------------------
        print("\n⏱ SCHEDULER"
              "\n------------------------")
        start_background(
            [PYTHON, SRC_DIR / "scheduler.py"],
            "Weather data scheduler",
        )

        # -----------------------------
        # REPORTING
        # -----------------------------
        print("\n📄 REPORTING"
              "\n------------------------")
        run_once(
            [PYTHON, SRC_DIR / "reporter.py"],
            "Daily report generation",
        )

        # -----------------------------
        # DASHBOARD
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