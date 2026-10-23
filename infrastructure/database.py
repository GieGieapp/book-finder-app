from pymongo import MongoClient, ASCENDING
from flask import current_app


class DatabaseManager:
    """Manages MongoDB client lifecycle and connection pooling"""

    def __init__(self, app=None):
        self.client = None
        self.db = None
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Initializes database connection from Flask application config and ensures indexes"""
        mongo_uri = app.config.get("MONGO_URI", "mongodb://localhost:27017/")
        db_name = app.config.get("MONGO_DB_NAME", "book_finder_db")
        self.client = MongoClient(mongo_uri)
        try:
            self.db = self.client.get_default_database()
        except Exception:
            self.db = self.client[db_name]

        # Ensure index on wishlist book ID for O(1) query performance
        try:
            self.db["wishlists"].create_index([("id", ASCENDING)], unique=True)
        except Exception:
            pass

        # Store database reference in Flask app context
        app.extensions["pymongo_db"] = self.db

    def get_db(self):
        """Retrieves active database instance"""
        if self.db is not None:
            return self.db
        if current_app and "pymongo_db" in current_app.extensions:
            return current_app.extensions["pymongo_db"]
        raise RuntimeError("Database not initialized via init_app().")


db_manager = DatabaseManager()


def get_db():
    return db_manager.get_db()
