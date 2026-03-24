from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


APP_NAME = "nemoclaw-control"


def log_dir() -> Path:
    path = Path.home() / ".local" / "state" / APP_NAME
    path.mkdir(parents=True, exist_ok=True)
    return path


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(APP_NAME)
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_dir() / "app.log", maxBytes=3_000_000, backupCount=3)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger
