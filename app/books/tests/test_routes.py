import unittest
from unittest.mock import patch
import json
from http import HTTPStatus
from flask import Flask

from app.books.routes import book_bp


class TestBookRoutes(unittest.TestCase):
    def setUp(self):
        # Create minimal isolated Flask application for route testing
        self.app = Flask(__name__)
        self.app.register_blueprint(book_bp)
        self.client = self.app.test_client()

    @patch("app.books.routes.book_service", autospec=True)
    def test_search_books_route_success_positive(self, mock_book_service):
        # Positive: Returns 200 OK and list of books when query is provided
        mock_book_service.search_books.return_value = [
            {"id": "1", "title": "Domain-Driven Design"}
        ]

        response = self.client.get("/api/search?q=ddd")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Domain-Driven Design")
        mock_book_service.search_books.assert_called_once_with("ddd")

    @patch("app.books.routes.book_service", autospec=True)
    def test_search_books_alternative_url_positive(self, mock_book_service):
        # Positive: Alternative URL /search returns 200 OK
        mock_book_service.search_books.return_value = [
            {"id": "2", "title": "Clean Code"}
        ]

        response = self.client.get("/search?q=clean")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_book_service.search_books.assert_called_once_with("clean")

    @patch("app.books.routes.book_service", autospec=True)
    def test_search_books_route_empty_query_negative(self, mock_book_service):
        # Negative: Empty query string returns 200 with empty list
        mock_book_service.search_books.return_value = []

        response = self.client.get("/api/search?q=")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.data)
        self.assertEqual(data, [])
        mock_book_service.search_books.assert_called_once_with("")

    @patch("app.books.routes.book_service", autospec=True)
    def test_search_books_route_missing_query_param_negative(self, mock_book_service):
        # Negative: Missing 'q' parameter defaults to empty string query
        mock_book_service.search_books.return_value = []

        response = self.client.get("/api/search")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.data)
        self.assertEqual(data, [])
        mock_book_service.search_books.assert_called_once_with("")

    def test_search_books_method_not_allowed_negative(self):
        # Negative: Non-GET method returns 405 Method Not Allowed
        response = self.client.post("/api/search")
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


if __name__ == "__main__":
    unittest.main()
