"""
Centralised logging configuration.

Creates a rotating-file handler and a stream handler so logs appear
both in the terminal (useful during development) and in a persistent
log file (useful in production).
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime

_LOGS_DIR = "logs"
os.makedirs(_LOGS_DIR, exist_ok=True)

_LOG_FILE = os.path.join(
    _LOGS_DIR, f"app_{datetime.now().strftime('%Y-%m-%d')}.log"
)

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Configure the root logger once
logging.basicConfig(
    level=logging.INFO,
    format=_LOG_FORMAT,
    datefmt=_DATE_FORMAT,
    handlers=[
        # Rotating file — max 5 MB, keep 3 backups
        RotatingFileHandler(
            _LOG_FILE,
            maxBytes=5 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        ),
        # Stream (console)
        logging.StreamHandler(),
    ],
)


def get_logger(name: str) -> logging.Logger:
    """Return a named logger that inherits the root configuration."""
    return logging.getLogger(name)
