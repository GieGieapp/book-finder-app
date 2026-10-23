import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base application configuration with sensible defaults"""
    SECRET_KEY = os.getenv("SECRET_KEY", "book-finder-secret-key-2026")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_db")
    GOOGLE_BOOKS_API_KEY = os.getenv("GOOGLE_BOOKS_API_KEY", "")
    GOOGLE_BOOKS_API_URL = os.getenv("GOOGLE_BOOKS_API_URL", "https://www.googleapis.com/books/v1/volumes")
    OPEN_LIBRARY_API_URL = os.getenv("OPEN_LIBRARY_API_URL", "https://openlibrary.org/search.json")
    HTTP_TIMEOUT = int(os.getenv("HTTP_TIMEOUT", 10))
    DEBUG = False
    TESTING = False


class DevelopmentConfig(Config):
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_dev")


class StagingConfig(Config):
    DEBUG = False
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://staging-mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_staging")


class ProductionConfig(Config):
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_prod")


class TestingConfig(Config):
    TESTING = True
    MONGO_DB_NAME = "book_finder_test_db"


_CONFIG_MAP = {
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


def get_config(env_name: str = None) -> type[Config]:
    """Resolves and returns appropriate Configuration class for the active environment"""
    env = (env_name or os.getenv("FLASK_ENV") or os.getenv("APP_ENV") or "development").strip().lower()
    return _CONFIG_MAP.get(env, DevelopmentConfig)
