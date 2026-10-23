from typing import List, Optional, Dict, Any
from infrastructure.database import get_db
from core.logger import get_logger
from core.constants import DEFAULT_EMPTY_DATE
from .models import WishlistItem

logger = get_logger(__name__)


class MongoWishlistRepository:
    """Repository for wishlist data persistence in MongoDB"""

    def __init__(self, db=None):
        self._db = db
        self._collection = db['wishlists'] if db is not None else None

    @property
    def collection(self):
        if self._collection is not None:
            return self._collection
        return get_db()['wishlists']

    def upsert(self, item: WishlistItem) -> None:
        """Inserts or updates a wishlist item by book ID"""
        self.collection.update_one(
            {"id": item.id},
            {"$set": item.to_dict()},
            upsert=True
        )

    def find_all(self) -> List[WishlistItem]:
        """Retrieves the complete list of wishlist items from database"""
        cursor = self.collection.find({}, {"_id": False})
        return [item for doc in cursor if (item := self._document_to_entity(doc))]

    def delete_by_id(self, book_id: str) -> bool:
        """Deletes a wishlist item by book ID"""
        clean_id = str(book_id).strip() if book_id else ""
        if not clean_id:
            return False
        result = self.collection.delete_one({"id": clean_id})
        return result.deleted_count > 0

    # --- Private Helper Parsers (Extract Method Pattern) ---

    def _document_to_entity(self, doc: Dict[str, Any]) -> Optional[WishlistItem]:
        """Converts a raw MongoDB document into a WishlistItem Entity"""
        try:
            return WishlistItem(
                id=doc.get("id", ""),
                title=doc.get("title", ""),
                authors=doc.get("authors", []),
                thumbnail=doc.get("thumbnail", ""),
                rating=float(doc.get("rating", 0.0)),
                description=doc.get("description", ""),
                published_date=doc.get("published_date") or DEFAULT_EMPTY_DATE,
                page_count=int(doc.get("page_count", 0)),
                categories=doc.get("categories", []),
                info_link=doc.get("info_link", "")
            )
        except Exception as exc:
            logger.warning("Failed to map MongoDB document to WishlistItem: %s", exc)
            return None
