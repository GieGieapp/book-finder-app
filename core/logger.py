import logging
import os
import sys

LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s]: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logging(app=None) -> None:
    """Configures centralized structured logging to stdout"""
    is_dev = os.getenv("FLASK_ENV", "development").lower() in ("dev", "development")
    level = logging.DEBUG if is_dev else logging.INFO

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers = [handler]

    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("werkzeug").setLevel(logging.INFO)


def get_logger(name: str) -> logging.Logger:
    """Returns a named logger instance"""
    return logging.getLogger(name)
