import os
from pathlib import Path

# Deteksi root directory proyek
BASE_DIR = Path(__file__).resolve().parent.parent

# Deteksi Environment aktif dari sistem (mendukung FLASK_ENV atau APP_ENV, default: development)
RAW_ENV = (os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development").strip().lower()

# Alias mapping agar singkatan seperti 'stg', 'prd', 'dev' otomatis dikenali
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

# Prioritas file env yang dicari:
# 1. .env.<nama_variasi> (misal .env.staging atau .env.stg)
# 2. .env (default fallback)
env_candidates = [BASE_DIR / f".env.{var}" for var in target_variants] + [BASE_DIR / ".env"]

try:
    from dotenv import load_dotenv
    # Muat file env yang paling spesifik yang ditemukan pertama kali
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
    """Base Configuration (Default untuk semua stage)"""
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
    1. LOCAL DEVELOPMENT (dev)
    - Debug mode aktif untuk hot-reload & error tracking
    - Database lokal: book_finder_dev
    - Auto reload templates HTML aktif
    """
    ENV_NAME = "development"
    DEBUG = True
    TEMPLATES_AUTO_RELOAD = True
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017/")
    MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "book_finder_dev")


class StagingConfig(Config):
    """
    2. STAGING / UAT SERVER (stg)
    - Debug mode NONAKTIF (meniru production)
    - Database terpisah untuk QA/UAT: book_finder_staging
    - Log error tetap detail untuk kemudahan debugging tim QA
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
    3. LIVE PRODUCTION (prd)
    - Debug mode NONAKTIF 100% (mencegah kebocoran traceback / data sensitif)
    - Database Production terproteksi: book_finder_prod
    - Proteksi keamanan cookie sesi (HttpOnly & SameSite Lax)
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
    4. AUTOMATED TESTING (test)
    - Mode testing aktif (Flask test client)
    - Database khusus testing terisolasi: book_finder_test_db
    """
    ENV_NAME = "testing"
    DEBUG = False
    TESTING = True
    MONGO_DB_NAME = "book_finder_test_db"


# Mapping Environment Name / Alias ke Configuration Class
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
    """Mengambil configuration class yang tepat berdasarkan nama environment"""
    if env_name is None:
        env_name = os.getenv("APP_ENV") or os.getenv("FLASK_ENV") or "development"
    return CONFIG_MAP.get(str(env_name).strip().lower(), DevelopmentConfig)

