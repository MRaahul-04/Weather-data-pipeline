import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import atexit

# Resolve project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / "pipeline.log"

# Create named logger
logger = logging.getLogger("weather-pipeline")
logger.setLevel(logging.INFO)

# Prevent duplicate handlers
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

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

# ✅ Option 2: Properly close handlers on exit (CRITICAL on Windows)
def _close_logging_handlers():
    for handler in logger.handlers:
        handler.close()
        logger.removeHandler(handler)

atexit.register(_close_logging_handlers)
