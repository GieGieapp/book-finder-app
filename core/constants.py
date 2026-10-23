APP_NAME = "BookFinderApp"
APP_VERSION = "1.0.0"
DEFAULT_USER_AGENT = f"{APP_NAME}/{APP_VERSION}"

# HTTP & Network Defaults
DEFAULT_TIMEOUT_SECONDS = 10
DEFAULT_SEARCH_LIMIT = 20

# Remote API Endpoints (Fallback Defaults)
DEFAULT_GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"
DEFAULT_OPEN_LIBRARY_API_URL = "https://openlibrary.org/search.json"
DEFAULT_OPEN_LIBRARY_FIELDS = "key,title,author_name,cover_i,ratings_average,first_publish_year,number_of_pages_median,subject"

# Data Defaults & Placeholders
DEFAULT_PLACEHOLDER_COVER = "https://via.placeholder.com/128x192?text=No+Cover"
DEFAULT_UNTITLED_BOOK = "Tanpa Judul"
DEFAULT_UNKNOWN_AUTHOR = "Penulis Tidak Diketahui"
DEFAULT_NO_DESCRIPTION = "Tidak ada ringkasan deskripsi tersedia."
DEFAULT_OPEN_LIBRARY_DESCRIPTION = "Informasi buku dari katalog Open Library."
DEFAULT_EMPTY_DATE = "-"
DEFAULT_MAX_DISPLAY_CATEGORIES = 3
