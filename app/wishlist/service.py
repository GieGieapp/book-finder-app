from typing import List, Optional, Dict, Any
from core.errors import DomainValidationError
from core.constants import (
    DEFAULT_UNKNOWN_AUTHOR,
    DEFAULT_PLACEHOLDER_COVER,
    DEFAULT_NO_DESCRIPTION,
    DEFAULT_EMPTY_DATE,
)
from core.logger import get_logger
from .models import WishlistItem
from .schemas import WishlistItemSchema
from .repository import MongoWishlistRepository

logger = get_logger(__name__)


class WishlistService:
    """Service for wishlist collection management use cases"""

    def __init__(self, repository: Optional[MongoWishlistRepository] = None):
        self.repository = repository or MongoWishlistRepository()

    def add_to_wishlist(self, data: dict) -> dict:
        """Adds a book to the wishlist after input sanitization and validation"""
        # 1. Parse & validate request payload into Domain Entity
        item = self._parse_request_payload(data)

        # 2. Persist to Database via Repository
        self.repository.upsert(item)
        logger.info("Book '%s' (ID: %s) successfully saved to wishlist", item.title, item.id)

        # 3. Return response data contract (Schema)
        return self._entity_to_schema(item).to_dict()

    def get_all_wishlists(self, limit: Optional[int] = None, skip: int = 0) -> List[dict]:
        """Retrieves all wishlist items as a list of schema dictionaries with optional pagination"""
        if limit is not None:
            items: List[WishlistItem] = self.repository.find_all(limit=limit, skip=skip)
        else:
            items: List[WishlistItem] = self.repository.find_all()
        return [self._entity_to_schema(item).to_dict() for item in items]

    def count_all_wishlists(self) -> int:
        """Returns total count of wishlist items in database"""
        if hasattr(self.repository, "count_all"):
            return self.repository.count_all()
        return len(self.get_all_wishlists())

    def get_wishlist_ids(self) -> List[str]:
        """Returns list of all book IDs in wishlist for membership check"""
        if hasattr(self.repository, "get_all_ids"):
            return self.repository.get_all_ids()
        return [item["id"] for item in self.get_all_wishlists() if "id" in item]

    def remove_from_wishlist(self, book_id: str) -> bool:
        """Removes a book from the wishlist by book ID"""
        clean_id = str(book_id).strip() if book_id else ""
        if not clean_id:
            return False

        if not self.repository.delete_by_id(clean_id):
            logger.warning("Failed to remove book ID '%s': not found in database", clean_id)
            return False

        logger.info("Book ID '%s' successfully removed from wishlist", clean_id)
        return True

    # --- Private Helper Parsers & Mappers ---

    def _parse_request_payload(self, data: Dict[str, Any]) -> WishlistItem:
        """Validates request payload structure and transforms it into a WishlistItem Entity"""
        if not isinstance(data, dict):
            raise DomainValidationError("Payload wishlist harus berupa JSON object.")

        required_fields = {
            "id": "ID buku wajib diisi.",
            "title": "Judul buku wajib diisi.",
        }
        for field, err_msg in required_fields.items():
            if not str(data.get(field, "")).strip():
                raise DomainValidationError(err_msg)

        book_id = str(data["id"]).strip()
        title = str(data["title"]).strip()

        authors = data.get("authors")
        if not isinstance(authors, list):
            authors = [str(authors)] if authors else [DEFAULT_UNKNOWN_AUTHOR]

        thumbnail = str(data.get("thumbnail", "")).strip()
        if thumbnail:
            thumbnail = thumbnail.replace("http://", "https://")
        else:
            thumbnail = DEFAULT_PLACEHOLDER_COVER

        try:
            rating = float(data.get("rating", 0.0))
        except (ValueError, TypeError):
            rating = 0.0

        return WishlistItem(
            id=book_id,
            title=title,
            authors=authors,
            thumbnail=thumbnail,
            rating=rating,
            description=str(data.get("description", DEFAULT_NO_DESCRIPTION)),
            published_date=str(data.get("published_date") or DEFAULT_EMPTY_DATE),
            page_count=int(data.get("page_count", 0)) if str(data.get("page_count", "")).isdigit() else 0,
            categories=data.get("categories", []) if isinstance(data.get("categories"), list) else [],
            info_link=str(data.get("info_link", ""))
        )

    def _entity_to_schema(self, item: WishlistItem) -> WishlistItemSchema:
        """Converts Domain Entity WishlistItem to Response Schema"""
        return WishlistItemSchema(
            id=item.id,
            title=item.title,
            authors=item.authors,
            thumbnail=item.thumbnail,
            rating=item.rating,
            description=item.description,
            published_date=item.published_date,
            page_count=item.page_count,
            categories=item.categories,
            info_link=item.info_link,
        )
