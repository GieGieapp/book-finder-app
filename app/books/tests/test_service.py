import unittest
from unittest.mock import MagicMock, create_autospec

from app.books.models import Book
from app.books.schemas import BookSchema, BookDTO
from app.books.repository import BookRepository
from app.books.service import GoogleBooksGateway, BookService


class TestBookModelsAndSchemas(unittest.TestCase):
    def test_book_entity_creation_positive(self):
        # Positive: Verify entity attributes and dictionary serialization
        book = Book(id="b_1", title="Clean Code", rating=4.9)
        self.assertEqual(book.id, "b_1")
        self.assertEqual(book.title, "Clean Code")
        self.assertEqual(book.rating, 4.9)
        self.assertEqual(book.to_dict()["title"], "Clean Code")

    def test_book_schema_contract_positive(self):
        # Positive: Verify schema conversion and DTO alias
        schema = BookSchema(id="schema_1", title="Refactoring", rating=4.5)
        self.assertEqual(schema.id, "schema_1")
        self.assertEqual(schema.to_dict()["title"], "Refactoring")

        dto = BookDTO(id="dto_1", title="Patterns")
        self.assertEqual(dto.id, "dto_1")


class TestBookService(unittest.TestCase):
    def test_search_books_success_positive(self):
        # Positive: Valid query calls repository and returns serialized schemas
        mock_repo = create_autospec(BookRepository)
        mock_repo.search.return_value = [
            Book(id="py_1", title="Fluent Python", authors=["Luciano Ramalho"], rating=4.8)
        ]

        service = BookService(repository=mock_repo)
        results = service.search_books("python")

        mock_repo.search.assert_called_once_with("python")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], "py_1")
        self.assertEqual(results[0]["title"], "Fluent Python")

    def test_search_books_empty_keyword_negative(self):
        # Negative: Empty query keyword returns empty list without querying repository
        mock_repo = create_autospec(BookRepository)
        service = BookService(repository=mock_repo)

        results = service.search_books("")
        self.assertEqual(results, [])
        mock_repo.search.assert_not_called()

    def test_search_books_whitespace_keyword_negative(self):
        # Negative: Whitespace query returns empty list without querying repository
        mock_repo = create_autospec(BookRepository)
        service = BookService(repository=mock_repo)

        results = service.search_books("     ")
        self.assertEqual(results, [])
        mock_repo.search.assert_not_called()


class TestBookRepository(unittest.TestCase):
    def test_search_calls_google_gateway_first_positive(self):
        # Positive: Returns books from primary provider (Google Books)
        mock_gateway = create_autospec(GoogleBooksGateway)
        mock_gateway.fetch_from_google.return_value = [
            {"id": "b_gateway", "volumeInfo": {"title": "Architecture Patterns"}}
        ]

        repo = BookRepository(gateway=mock_gateway)
        books = repo.search("architecture")

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, "b_gateway")
        self.assertEqual(books[0].title, "Architecture Patterns")
        mock_gateway.fetch_from_google.assert_called_once_with("architecture")
        mock_gateway.fetch_from_open_library.assert_not_called()

    def test_search_falls_back_to_open_library_positive(self):
        # Positive: Falls back to secondary provider (Open Library) when Google Books yields empty results
        mock_gateway = create_autospec(GoogleBooksGateway)
        mock_gateway.fetch_from_google.return_value = []
        mock_gateway.fetch_from_open_library.return_value = [
            {
                "key": "/works/OL123W",
                "title": "Open Library Book",
                "subject": ["Tag1", "Tag2", "Tag3", "Tag4", "Tag5"]
            }
        ]

        repo = BookRepository(gateway=mock_gateway)
        books = repo.search("fallback")

        self.assertEqual(len(books), 1)
        self.assertEqual(books[0].id, "ol_OL123W")
        self.assertEqual(len(books[0].categories), 3)
        self.assertEqual(books[0].categories, ["Tag1", "Tag2", "Tag3"])
        mock_gateway.fetch_from_google.assert_called_once_with("fallback")
        mock_gateway.fetch_from_open_library.assert_called_once_with("fallback")

    def test_search_empty_keyword_returns_empty_list_negative(self):
        # Negative: Empty or None keyword returns empty list immediately
        mock_gateway = create_autospec(GoogleBooksGateway)
        repo = BookRepository(gateway=mock_gateway)

        self.assertEqual(repo.search(""), [])
        self.assertEqual(repo.search("   "), [])
        mock_gateway.fetch_from_google.assert_not_called()

    def test_search_both_gateways_empty_negative(self):
        # Negative: When both providers return empty results, repository returns empty list
        mock_gateway = create_autospec(GoogleBooksGateway)
        mock_gateway.fetch_from_google.return_value = []
        mock_gateway.fetch_from_open_library.return_value = []

        repo = BookRepository(gateway=mock_gateway)
        books = repo.search("nonexistent")

        self.assertEqual(books, [])
        mock_gateway.fetch_from_google.assert_called_once_with("nonexistent")
        mock_gateway.fetch_from_open_library.assert_called_once_with("nonexistent")

    def test_parse_google_item_missing_id_negative(self):
        # Negative: Google Books item missing id field is skipped
        repo = BookRepository()
        parsed = repo._parse_google_item({"volumeInfo": {"title": "Missing ID"}})
        self.assertIsNone(parsed)

    def test_parse_open_library_doc_missing_key_negative(self):
        # Negative: Open Library document missing key field is skipped
        repo = BookRepository()
        parsed = repo._parse_open_library_doc({"title": "Missing Key"})
        self.assertIsNone(parsed)


class TestGoogleBooksGateway(unittest.TestCase):
    def test_fetch_from_google_positive(self):
        # Positive: Gateway parses response and returns item list
        gateway = GoogleBooksGateway()
        gateway.get_json = MagicMock(return_value={"items": [{"id": "item1"}]})

        items = gateway.fetch_from_google("microservices")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["id"], "item1")

    def test_fetch_from_google_invalid_response_negative(self):
        # Negative: Returns empty list if gateway receives non-dict response
        gateway = GoogleBooksGateway()
        gateway.get_json = MagicMock(return_value=None)

        items = gateway.fetch_from_google("error_query")
        self.assertEqual(items, [])

    def test_fetch_from_open_library_positive(self):
        # Positive: Gateway parses docs from Open Library response
        gateway = GoogleBooksGateway()
        gateway.get_json = MagicMock(return_value={"docs": [{"key": "/works/123"}]})

        docs = gateway.fetch_from_open_library("devops")
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0]["key"], "/works/123")

    def test_fetch_from_open_library_invalid_response_negative(self):
        # Negative: Returns empty list if Open Library returns unexpected payload
        gateway = GoogleBooksGateway()
        gateway.get_json = MagicMock(return_value="unexpected string")

        docs = gateway.fetch_from_open_library("error_query")
        self.assertEqual(docs, [])


if __name__ == "__main__":
    unittest.main()
