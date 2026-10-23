import os
from typing import Type
from dotenv import load_dotenv

from .constants import (
    DEFAULT_GOOGLE_BOOKS_API_URL,
    DEFAULT_OPEN_LIBRARY_API_URL,
    DEFAULT_TIMEOUT_SECONDS,
)

load_dotenv()


class Config:
    """Base application configuration with standard defaults"""
    ENV_NAME = "base"
    SECRET_KEY = os.getenv("SECRET_KEY", "book-finder-secret-key-2026")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_db")
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    GOOGLE_BOOKS_API_URL = os.getenv("GOOGLE_BOOKS_API_URL", DEFAULT_GOOGLE_BOOKS_API_URL)
    OPEN_LIBRARY_API_URL = os.getenv("OPEN_LIBRARY_API_URL", DEFAULT_OPEN_LIBRARY_API_URL)
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", DEFAULT_TIMEOUT_SECONDS))
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    ENV_NAME = "development"
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_dev")


class StagingConfig(Config):
    ENV_NAME = "staging"
    DEBUG = False
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://staging-mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_staging")


class ProductionConfig(Config):
    ENV_NAME = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_prod")


class TestingConfig(Config):
    ENV_NAME = "testing"
    TESTING = True
    MONGO_DB_NAME = "book_finder_test_db"


_CONFIGS: dict[str, Type[Config]] = {
    "development": DevelopmentConfig,
    "dev": DevelopmentConfig,
    "local": DevelopmentConfig,
    "staging": StagingConfig,
    "stg": StagingConfig,
    "production": ProductionConfig,
    "prod": ProductionConfig,
    "prd": ProductionConfig,
    "testing": TestingConfig,
    "test": TestingConfig,
}


def get_config(env_name: str | None = None) -> Type[Config]:
    """Factory resolving appropriate Configuration class from environment name"""
    env = (env_name or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development").strip().lower()
    return _CONFIGS.get(env, DevelopmentConfig)
