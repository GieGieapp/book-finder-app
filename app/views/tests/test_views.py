import unittest
from unittest.mock import patch
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
    @patch("app.db_manager.ping", return_value=True)
    def test_health_check_healthy_positive(self, mock_ping):
        # Positive: Returns status healthy when database responds to ping
        with patch("infrastructure.database.db_manager.init_app"):
            app = create_app()
            client = app.test_client()

            response = client.get("/health")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.data)
            self.assertEqual(data["status"], "healthy")
            self.assertEqual(data["database"], "connected")
            mock_ping.assert_called_once()

    @patch("app.db_manager.ping", return_value=False)
    def test_health_check_degraded_negative(self, mock_ping):
        # Negative: Returns status degraded when database is unreachable
        with patch("infrastructure.database.db_manager.init_app"):
            app = create_app()
            client = app.test_client()

            response = client.get("/health")
            self.assertEqual(response.status_code, HTTPStatus.OK)
            data = json.loads(response.data)
            self.assertEqual(data["status"], "degraded")
            self.assertEqual(data["database"], "disconnected")
            mock_ping.assert_called_once()


if __name__ == "__main__":
    unittest.main()
