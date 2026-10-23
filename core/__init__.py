"""
Core Application Foundation
Pusat konfigurasi, konstanta, penanganan error, dan structured logging internal.
"""
from .config import get_config, Config
from .errors import register_error_handlers, DomainValidationError
from .logger import setup_logging, get_logger
from . import constants

# Backward compatibility alias ke infrastructure
from infrastructure.database import db_manager, get_db
from infrastructure.http_client import BaseHttpClient

__all__ = [
    "get_config",
    "Config",
    "register_error_handlers",
    "DomainValidationError",
    "setup_logging",
    "get_logger",
    "constants",
    # Aliases
    "db_manager",
    "get_db",
    "BaseHttpClient",
]
