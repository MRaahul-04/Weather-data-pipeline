# stop_app.py
# This script safely stops all running components of the Weather Data Pipeline system.
import psutil
import sys

# List of process identifiers to target for termination
TARGET_PROCESSES = [
    "streamlit",
    "scheduler.py",
    "run_app.py",
]

# Print shutdown initiation message
print("\n🛑 Stopping Weather Data Pipeline System...\n")

killed = set()

# Iterate over all running processes
for proc in psutil.process_iter(["pid", "name", "cmdline"]):
    try:
        cmdline = " ".join(proc.info["cmdline"] or [])
        # Check if the process command line matches any target identifier
        for target in TARGET_PROCESSES:
            if target in cmdline and proc.pid not in killed:
                # Terminate the matching process
                proc.terminate()
                # Track already-terminated process IDs to avoid duplicates
                killed.add(proc.pid)
                print(f"✔ Stopped process PID={proc.pid}")
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        continue

# Print shutdown confirmation message
print("\n✅ Weather Data Pipeline System stopped safely")
sys.exit(0)