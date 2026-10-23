import os
from typing import List, Dict, Any, Optional

from core.constants import (
    DEFAULT_GOOGLE_BOOKS_API_URL,
    DEFAULT_OPEN_LIBRARY_API_URL,
    DEFAULT_OPEN_LIBRARY_FIELDS,
    DEFAULT_SEARCH_LIMIT,
)
from core.logger import get_logger
from infrastructure.http_client import BaseHttpClient
from .models import Book
from .schemas import BookSchema

logger = get_logger(__name__)


class GoogleBooksGateway(BaseHttpClient):
    """
    HTTP Client for remote external book providers.
    Inherits centralized BaseHttpClient for automated timeout, headers, and error logging.
    """

    def __init__(
        self,
        google_books_url: Optional[str] = None,
        open_library_url: Optional[str] = None,
        timeout: Optional[int] = None,
        api_key: Optional[str] = None,
        user_agent: Optional[str] = None,
    ):
        super().__init__(timeout=timeout, user_agent=user_agent)
        self.google_books_url = google_books_url or os.getenv("GOOGLE_BOOKS_API_URL", DEFAULT_GOOGLE_BOOKS_API_URL)
        self.open_library_url = open_library_url or os.getenv("OPEN_LIBRARY_API_URL", DEFAULT_OPEN_LIBRARY_API_URL)
        self.api_key = api_key if api_key is not None else os.getenv("GOOGLE_BOOKS_API_KEY", "").strip()

    def fetch_from_google(self, keyword: str, max_results: int = DEFAULT_SEARCH_LIMIT) -> List[Dict[str, Any]]:
        """Executes pure HTTP GET to Google Books API and returns raw items"""
        params = {"q": keyword, "maxResults": max_results}
        if self.api_key:
            params["key"] = self.api_key

        data = self.get_json(self.google_books_url, params=params)
        return data.get("items", []) if isinstance(data, dict) else []

    def fetch_from_open_library(self, keyword: str, limit: int = DEFAULT_SEARCH_LIMIT) -> List[Dict[str, Any]]:
        """Executes optimized HTTP GET to Open Library API and returns raw docs"""
        params = {
            "q": keyword,
            "limit": limit,
            "fields": DEFAULT_OPEN_LIBRARY_FIELDS,
        }
        data = self.get_json(self.open_library_url, params=params)
        return data.get("docs", []) if isinstance(data, dict) else []


class BookService:
    """
    Use Case: Orchestrates book catalog search.
    Fetches Domain Entities (Book) from Repository, transforms them
    into Response Schemas (BookSchema) for the Controller.
    """

    def __init__(self, repository=None):
        if repository is None:
            from .repository import BookRepository
            self.repository = BookRepository()
        else:
            self.repository = repository

    def search_books(self, keyword: str) -> List[dict]:
        clean_keyword = keyword.strip() if keyword else ""
        if not clean_keyword:
            return []

        logger.info("Starting book search with keyword: '%s'", clean_keyword)

        # 1. Query external APIs via Repository to obtain Domain Entities (Book)
        books: List[Book] = self.repository.search(clean_keyword)

        # 2. Transform: Entity (Book) -> Response Schema (BookSchema)
        schemas: List[BookSchema] = [
            BookSchema(
                id=book.id,
                title=book.title,
                authors=book.authors,
                thumbnail=book.thumbnail,
                rating=book.rating,
                description=book.description,
                published_date=book.published_date,
                page_count=book.page_count,
                categories=book.categories,
                info_link=book.info_link
            )
            for book in books
        ]

        logger.info("Search completed. Found %d books.", len(schemas))

        # 3. Return JSON-serializable dictionaries to Controller
        return [s.to_dict() for s in schemas]
