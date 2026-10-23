from typing import Final

# Application Metadata
APP_NAME: Final[str] = "BookFinderApp"
APP_VERSION: Final[str] = "1.0.0"
DEFAULT_USER_AGENT: Final[str] = f"{APP_NAME}/{APP_VERSION}"

# HTTP & Network Defaults
DEFAULT_TIMEOUT_SECONDS: Final[int] = 10
DEFAULT_SEARCH_LIMIT: Final[int] = 20

# Remote API Defaults
DEFAULT_GOOGLE_BOOKS_API_URL: Final[str] = "https://www.googleapis.com/books/v1/volumes"
DEFAULT_OPEN_LIBRARY_API_URL: Final[str] = "https://openlibrary.org/search.json"
DEFAULT_OPEN_LIBRARY_FIELDS: Final[str] = "key,title,author_name,cover_i,ratings_average,first_publish_year,number_of_pages_median,subject"

# Domain Fallback Values
DEFAULT_PLACEHOLDER_COVER: Final[str] = "https://via.placeholder.com/128x192?text=No+Cover"
DEFAULT_UNTITLED_BOOK: Final[str] = "Untitled"
DEFAULT_UNKNOWN_AUTHOR: Final[str] = "Unknown Author"
DEFAULT_NO_DESCRIPTION: Final[str] = "No description available."
DEFAULT_OPEN_LIBRARY_DESCRIPTION: Final[str] = "Book information from Open Library catalog."
DEFAULT_EMPTY_DATE: Final[str] = "-"
DEFAULT_MAX_DISPLAY_CATEGORIES: Final[int] = 3
