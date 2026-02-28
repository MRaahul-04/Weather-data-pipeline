# This module configures centralized application logging with rotation.

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import atexit

# Resolve project root and log directory path for storing log files
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"

# Create named logger for the application
logger = logging.getLogger("weather-pipeline")
# Set default log level to INFO
logger.setLevel(logging.INFO)

# Prevent duplicate handlers (important for imports & reloads)
if not logger.handlers:
    # Rotating file handler (BEST PRACTICE)
    file_handler = RotatingFileHandler(
        LOG_FILE,
        mode="a",                 # ✅ Option 1: Append mode
        maxBytes=5 * 1024 * 1024, # 5 MB per file
        backupCount=5,            # Keep last 5 logs
        encoding="utf-8",
        delay=True                # File opened only when first log is written
    )

    # Define log message format: timestamp, level, logger name, message
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

# Graceful shutdown of logging handlers on exit (critical for Windows)
def _close_logging_handlers():
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

atexit.register(_close_logging_handlers)
