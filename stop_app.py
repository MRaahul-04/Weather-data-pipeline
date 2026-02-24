import psutil
import sys

TARGET_PROCESSES = [
    "streamlit",
    "scheduler.py",
    "run_app.py",
]

print("\n🛑 Stopping Weather Data Pipeline System...\n")

killed = set()

for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        cmdline = " ".join(proc.info["cmdline"] or [])
        for target in TARGET_PROCESSES:
            if target in cmdline and proc.pid not in killed:
                proc.terminate()
                killed.add(proc.pid)
                print(f"✔ Stopped process PID={proc.pid}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

print("\n✅ Weather Data Pipeline System stopped safely")
sys.exit(0)