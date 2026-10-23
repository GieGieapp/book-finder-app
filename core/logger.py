import logging
import os
import sys
from typing import Optional

LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(app=None, log_level: Optional[int] = None) -> None:
    """Configures centralized structured logging to stdout"""
    if log_level is None:
        is_dev = os.getenv("FLASK_ENV", "development").lower() in ("dev", "development")
        log_level = logging.DEBUG if is_dev else logging.INFO

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(log_level)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers = [handler]

    # Silence noisy external library logs
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Returns a namespaced logger instance"""
    return logging.getLogger(name)
