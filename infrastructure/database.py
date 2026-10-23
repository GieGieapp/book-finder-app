from typing import Optional
from pymongo import MongoClient, ASCENDING
from pymongo.database import Database
from flask import current_app, Flask


class DatabaseManager:
    """Manages MongoDB connection pooling, indexing, and lifecycle"""

    def __init__(self, app: Optional[Flask] = None):
        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        if app:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initializes database connection from Flask application config and ensures indexes"""
        mongo_uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/")
        db_name = app.config.get("MONGO_DB_NAME", "book_finder_db")
        self.client = MongoClient(mongo_uri)

        try:
            self.db = self.client.get_default_database()
        except Exception:
            self.db = self.client[db_name]

        self._ensure_indexes()
        app.extensions["pymongo_db"] = self.db

    def get_db(self) -> Database:
        """Returns the active MongoDB database instance"""
        if self.db is not None:
            return self.db
        if current_app and "pymongo_db" in current_app.extensions:
            return current_app.extensions["pymongo_db"]
        raise RuntimeError("Database not initialized. Call init_app() first.")

    def ping(self) -> bool:
        """Health check probe: pings MongoDB server. Returns True if alive, False otherwise."""
        try:
            db = self.get_db()
            db.command("ping")
            return True
        except Exception:
            return False

    def close(self) -> None:
        """Closes active client connection pool"""
        if self.client:
            self.client.close()

    def _ensure_indexes(self) -> None:
        """Ensures database indexes exist for high-performance lookups"""
        try:
            if self.db is not None:
                self.db["wishlists"].create_index([("id", ASCENDING)], unique=True)
        except Exception:
            pass


db_manager = DatabaseManager()


def get_db() -> Database:
    """Convenience accessor for current active database"""
    return db_manager.get_db()
