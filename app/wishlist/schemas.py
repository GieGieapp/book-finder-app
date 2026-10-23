from dataclasses import dataclass, field, asdict
from typing import List
from core.constants import (
    DEFAULT_UNKNOWN_AUTHOR,
    DEFAULT_PLACEHOLDER_COVER,
    DEFAULT_NO_DESCRIPTION,
    DEFAULT_EMPTY_DATE,
)


@dataclass
class WishlistItemSchema:
    """
    Data transfer schema for wishlist items returned to client/frontend.
    Pure data contract without business logic or entity conversion methods.
    """
    id: str
    title: str
    authors: List[str] = field(default_factory=lambda: [DEFAULT_UNKNOWN_AUTHOR])
    thumbnail: str = DEFAULT_PLACEHOLDER_COVER
    rating: float = 0.0
    description: str = DEFAULT_NO_DESCRIPTION
    published_date: str = DEFAULT_EMPTY_DATE
    page_count: int = 0
    categories: List[str] = field(default_factory=list)
    info_link: str = ""

    def to_dict(self) -> dict:
        """Converts schema to a JSON-serializable dictionary representation"""
        return asdict(self)


# Compatibility alias
WishlistItemDTO = WishlistItemSchema
