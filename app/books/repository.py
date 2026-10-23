from typing import List, Optional, Dict, Any
from core.constants import (
    DEFAULT_UNTITLED_BOOK,
    DEFAULT_UNKNOWN_AUTHOR,
    DEFAULT_PLACEHOLDER_COVER,
    DEFAULT_NO_DESCRIPTION,
    DEFAULT_OPEN_LIBRARY_DESCRIPTION,
    DEFAULT_EMPTY_DATE,
    DEFAULT_MAX_DISPLAY_CATEGORIES,
)
from .models import Book


class BookRepository:
    """Domain book catalog data repository provider"""

    def __init__(self, gateway=None):
        self._gateway = gateway

    @property
    def gateway(self):
        if self._gateway is None:
            from .service import GoogleBooksGateway
            self._gateway = GoogleBooksGateway()
        return self._gateway

    def search(self, keyword: str, start_index: int = 0) -> List[Book]:
        """Searches book catalog via Gateway and returns results as Domain Entity collection"""
        if not keyword or not keyword.strip():
            return []

        clean_keyword = keyword.strip()

        # 1. Query data via Google Books Gateway
        raw_items = self.gateway.fetch_from_google(clean_keyword, start_index=start_index)
        if raw_items:
            books = [b for item in raw_items if (b := self._parse_google_item(item))]
            if books:
                return books

        # 2. Fallback via Open Library Gateway
        raw_docs = self.gateway.fetch_from_open_library(clean_keyword, offset=start_index)
        if raw_docs:
            books = [b for doc in raw_docs if (b := self._parse_open_library_doc(doc))]
            if books:
                return books

        return []

    # --- Private Helper Parsers (Extract Method Pattern) ---

    def _parse_google_item(self, item: Dict[str, Any]) -> Optional[Book]:
        """Converts a raw Google Books item into a Book Entity"""
        bid = str(item.get("id", "")).strip()
        if not bid:
            return None

        vinfo = item.get("volumeInfo", {})
        authors = vinfo.get("authors") or [DEFAULT_UNKNOWN_AUTHOR]
        if not isinstance(authors, list):
            authors = [str(authors)]

        img_links = vinfo.get("imageLinks", {})
        thumb = img_links.get("thumbnail") or img_links.get("smallThumbnail")
        if thumb:
            thumb = thumb.replace("http://", "https://")
        else:
            thumb = DEFAULT_PLACEHOLDER_COVER

        try:
            rating = float(vinfo.get("averageRating", 0.0))
        except (ValueError, TypeError):
            rating = 0.0

        raw_cats = vinfo.get("categories")
        categories = [str(c) for c in raw_cats] if isinstance(raw_cats, list) else []

        return Book(
            id=bid,
            title=vinfo.get("title") or DEFAULT_UNTITLED_BOOK,
            authors=authors,
            thumbnail=thumb,
            rating=rating,
            description=vinfo.get("description") or DEFAULT_NO_DESCRIPTION,
            published_date=str(vinfo.get("publishedDate") or DEFAULT_EMPTY_DATE),
            page_count=int(vinfo.get("pageCount", 0)) if str(vinfo.get("pageCount", "")).isdigit() else 0,
            categories=categories,
            info_link=str(vinfo.get("infoLink", ""))
        )

    def _parse_open_library_doc(self, doc: Dict[str, Any]) -> Optional[Book]:
        """Converts a raw Open Library document into a Book Entity"""
        raw_key = doc.get("key", "").replace("/works/", "")
        if not raw_key:
            return None

        authors = doc.get("author_name") or [DEFAULT_UNKNOWN_AUTHOR]
        if not isinstance(authors, list):
            authors = [str(authors)]

        cover_id = doc.get("cover_i")
        thumb = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg" if cover_id else DEFAULT_PLACEHOLDER_COVER

        try:
            rating = round(float(doc.get("ratings_average", 0.0)), 1)
        except (ValueError, TypeError):
            rating = 0.0

        raw_subjects = doc.get("subject")
        categories = (
            [str(s) for s in raw_subjects[:DEFAULT_MAX_DISPLAY_CATEGORIES]]
            if isinstance(raw_subjects, list)
            else []
        )

        return Book(
            id=f"ol_{raw_key}",
            title=doc.get("title") or DEFAULT_UNTITLED_BOOK,
            authors=authors,
            thumbnail=thumb,
            rating=rating,
            description=DEFAULT_OPEN_LIBRARY_DESCRIPTION,
            published_date=str(doc.get("first_publish_year") or DEFAULT_EMPTY_DATE),
            page_count=int(doc.get("number_of_pages_median", 0) or 0),
            categories=categories,
            info_link=f"https://openlibrary.org{doc.get('key', '')}"
        )


# Compatibility alias
GoogleBooksRepository = BookRepository
