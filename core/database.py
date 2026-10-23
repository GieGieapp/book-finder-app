"""
Compatibility Bridge
Database management has moved to infrastructure.database
"""
from infrastructure.database import DatabaseManager, db_manager, get_db

__all__ = ["DatabaseManager", "db_manager", "get_db"]
