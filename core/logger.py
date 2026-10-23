import logging
import os
import sys
from typing import Optional


LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(app=None, log_level: Optional[str] = None) -> None:
    """
    Initializes centralized structured logging configuration for the entire application.
    Executes once during application bootstrap (create_app).
    """
    if log_level is None:
        flask_env = os.getenv("FLASK_ENV", "development").lower()
        log_level = logging.DEBUG if flask_env in ("dev", "development", "local") else logging.INFO
    elif isinstance(log_level, str):
        log_level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    if not root_logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        handler.setLevel(log_level)
        root_logger.addHandler(handler)
    else:
        for handler in root_logger.handlers:
            handler.setFormatter(formatter)
            handler.setLevel(log_level)

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Returns a namespaced logger instance"""
    return logging.getLogger(name)
