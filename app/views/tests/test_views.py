import unittest
from unittest.mock import patch, MagicMock
import json
from http import HTTPStatus
from flask import Flask

from app import create_app
from app.views.routes import view_bp


class TestViewsModule(unittest.TestCase):
    def setUp(self):
        # Create minimal isolated Flask application for view testing
        self.app = Flask(__name__)
        self.app.register_blueprint(view_bp)
        self.client = self.app.test_client()

    def test_index_page_loads_positive(self):
        # Positive: Index page loads successfully with 200 OK and returns HTML content
        response = self.client.get("/")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(b"Book Finder App", response.data)

    def test_index_page_method_not_allowed_negative(self):
        # Negative: Non-GET method on index route returns 405 Method Not Allowed
        response = self.client.post("/")
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)

    def test_nonexistent_route_returns_404_negative(self):
        # Negative: Accessing an unmapped path returns 404 Not Found
        response = self.client.get("/non-existent-view-path")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)


class TestHealthCheckEndpoint(unittest.TestCase):
    @patch("app.get_db")
    def test_health_check_healthy_positive(self, mock_get_db):
        # Positive: Returns status healthy when database responds to ping
        mock_db = MagicMock()
        mock_db.command.return_value = {"ok": 1.0}
        mock_get_db.return_value = mock_db

        with patch("infrastructure.database.db_manager.init_app"):
            app = create_app()
            client = app.test_client()

            response = client.get("/health")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.data)
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["database"], "connected")

    @patch("app.get_db")
    def test_health_check_degraded_negative(self, mock_get_db):
        # Negative: Returns status degraded when database is unreachable
        mock_get_db.side_effect = Exception("Database connection failure")

        with patch("infrastructure.database.db_manager.init_app"):
            app = create_app()
            client = app.test_client()

            response = client.get("/health")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.data)
            self.assertEqual(data["status"], "degraded")
            self.assertEqual(data["database"], "disconnected")


if __name__ == "__main__":
    unittest.main()
