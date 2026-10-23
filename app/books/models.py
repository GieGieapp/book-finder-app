from dataclasses import dataclass, field, asdict
from typing import List
from core.constants import (
    DEFAULT_UNTITLED_BOOK,
    DEFAULT_UNKNOWN_AUTHOR,
    DEFAULT_PLACEHOLDER_COVER,
    DEFAULT_NO_DESCRIPTION,
    DEFAULT_EMPTY_DATE,
)


@dataclass
class Book:
    """
    Pure Domain Entity representing a book catalog item in the application.
    Following Clean Architecture principles, this entity has zero dependencies
    on external vendors (Google Books / Open Library).
    """
    id: str
    title: str = DEFAULT_UNTITLED_BOOK
    authors: List[str] = field(default_factory=lambda: [DEFAULT_UNKNOWN_AUTHOR])
    thumbnail: str = DEFAULT_PLACEHOLDER_COVER
    rating: float = 0.0
    description: str = DEFAULT_NO_DESCRIPTION
    published_date: str = DEFAULT_EMPTY_DATE
    page_count: int = 0
    categories: List[str] = field(default_factory=list)
    info_link: str = ""

    def to_dict(self) -> dict:
        """Converts the entity to a pure dictionary representation"""
        return asdict(self)
