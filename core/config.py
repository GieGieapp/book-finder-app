import os
from pathlib import Path

# Resolve project root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Detect active runtime environment (supports FLASK_ENV or APP_ENV, defaults to development)
RAW_ENV = (os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development").strip().lower()

# Environment alias mapping for standard abbreviation recognition
ENV_ALIASES = {
    "dev": ("development", "dev"),
    "development": ("development", "dev"),
    "local": ("development", "dev"),
    "stg": ("staging", "stg", "uat"),
    "staging": ("staging", "stg", "uat"),
    "uat": ("staging", "stg", "uat"),
    "prd": ("production", "prd", "prod"),
    "prod": ("production", "prd", "prod"),
    "production": ("production", "prd", "prod"),
    "live": ("production", "prd", "prod"),
    "test": ("testing", "test"),
    "testing": ("testing", "test"),
}

target_variants = ENV_ALIASES.get(RAW_ENV, (RAW_ENV,))

# Candidate .env files prioritized by specificity
env_candidates = [BASE_DIR / f".env.{var}" for var in target_variants] + [BASE_DIR / ".env"]

try:
    from dotenv import load_dotenv
    # Load the most specific matching environment file
    for env_path in env_candidates:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=True)
            break
except ImportError:
    pass

from .constants import (
    DEFAULT_GOOGLE_BOOKS_API_URL,
    DEFAULT_OPEN_LIBRARY_API_URL,
    DEFAULT_TIMEOUT_SECONDS,
)


class Config:
    """Base Configuration (Defaults across all environments)"""
    ENV_NAME = "base"
    SECRET_KEY = os.getenv("SECRET_KEY", "book-finder-super-secret-key-2026")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_db")
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    GOOGLE_BOOKS_API_URL = os.getenv("GOOGLE_BOOKS_API_URL", DEFAULT_GOOGLE_BOOKS_API_URL)
    OPEN_LIBRARY_API_URL = os.getenv("OPEN_LIBRARY_API_URL", DEFAULT_OPEN_LIBRARY_API_URL)
    EXTERNAL_API_TIMEOUT = int(os.getenv("EXTERNAL_API_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS)))
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False


class DevelopmentConfig(Config):
    """
    Local Development Environment (dev)
    - Debug mode enabled for hot-reloading and tracing
    - Dedicated development database: book_finder_dev
    - HTML templates auto-reload enabled
    """
    ENV_NAME = "development"
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_dev")


class StagingConfig(Config):
    """
    Staging / UAT Environment (stg)
    - Debug mode disabled (mirrors production behavior)
    - Isolated QA/UAT database: book_finder_staging
    - Detailed error logging preserved for QA diagnostics
    """
    ENV_NAME = "staging"
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    PROPAGATE_EXCEPTIONS = True
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://staging-mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_staging")


class ProductionConfig(Config):
    """
    Live Production Environment (prd)
    - Strict debug mode disabled (prevents sensitive traceback exposure)
    - Production database: book_finder_prod
    - Enhanced session cookie security (HttpOnly, Secure, SameSite)
    """
    ENV_NAME = "production"
    DEBUG = False
    TESTING = False
    TEMPLATES_AUTO_RELOAD = False
    PROPAGATE_EXCEPTIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://prod_cluster.mongodb.net/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_prod")


class TestingConfig(Config):
    """
    Automated Testing Environment (test)
    - Flask testing mode enabled
    - Isolated in-memory/test database: book_finder_test_db
    """
    ENV_NAME = "testing"
    DEBUG = False
    TESTING = True
    MONGO_DB_NAME = "book_finder_test_db"


# Environment Name / Alias to Configuration Class Mapping
CONFIG_MAP = {
    # Development aliases
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "local": DevelopmentConfig,

    # Staging aliases
    "staging": StagingConfig,
    "stg": StagingConfig,
    "uat": StagingConfig,

    # Production aliases
    "production": ProductionConfig,
    "prod": ProductionConfig,
    "prd": ProductionConfig,
    "live": ProductionConfig,

    # Testing aliases
    "testing": TestingConfig,
    "test": TestingConfig,
}


def get_config(env_name=None):
    """Resolves and returns appropriate Configuration class for target environment"""
    if env_name is None:
        env_name = os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development"
    return CONFIG_MAP.get(str(env_name).strip().lower(), DevelopmentConfig)
