"""
Logger configuration module.

Sets up both console and rotating file logging handlers using Python's
built-in `logging` module. Reads configuration from the settings module.
"""

import logging
from logging.handlers import RotatingFileHandler
from config.settings import settings
import os

# Ensure the logs directory exists
os.makedirs(settings.LOG_FILE.parent, exist_ok=True)

# Configure root logger
logger = logging.getLogger("Logger")
logger.setLevel(settings.LOG_LEVEL)

# Console Handler Configuration
console_handler = logging.StreamHandler()
console_handler.setLevel(settings.LOG_LEVEL)
console_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)

# Rotating File Handler Configuration
file_handler = RotatingFileHandler(
    filename=settings.LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB per file
    backupCount=5,  # Keep up to 5 backup logs
)
file_handler.setLevel(settings.LOG_LEVEL)
file_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)
