"""
Logger configuration module.

Sets up both console and rotating file logging handlers using Python's
built-in `logging` module. Reads configuration from the settings module.
"""

import logging
import os
import sys

from logging.handlers import RotatingFileHandler

from settings import settings

# Ensure the logs directory exists
os.makedirs(settings.LOG_FILE.parent, exist_ok=True)

# Configure root logger
logger = logging.getLogger("Logger")
logger.setLevel(settings.LOG_LEVEL)

# Console Handler Configuration
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(settings.LOG_LEVEL)
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)

# Try to set UTF-8 encoding for the console stream
if hasattr(console_handler.stream, "reconfigure"):
    try:
        console_handler.stream.reconfigure(encoding="utf-8")
    except (AttributeError, TypeError, ValueError):
        pass  # Ignore if not supported

logger.addHandler(console_handler)

# Rotating File Handler Configuration
file_handler = RotatingFileHandler(
    filename=settings.LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB per file
    backupCount=5,  # Keep up to 5 backup logs
    encoding="utf-8",
)
file_handler.setLevel(settings.LOG_LEVEL)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
