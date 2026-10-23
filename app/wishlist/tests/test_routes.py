import unittest
from unittest.mock import patch
import json
from http import HTTPStatus
from flask import Flask

from core.errors import DomainValidationError
from app.wishlist.routes import wishlist_bp


class TestWishlistRoutes(unittest.TestCase):
    def setUp(self):
        # Create minimal isolated Flask application for route testing
        self.app = Flask(__name__)
        self.app.register_blueprint(wishlist_bp)
        self.client = self.app.test_client()

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_get_wishlists_success_positive(self, mock_wishlist_service):
        # Positive: Returns 200 OK and list of saved wishlist items
        mock_wishlist_service.get_all_wishlists.return_value = [
            {"id": "w_1", "title": "Clean Code"}
        ]

        response = self.client.get("/api/wishlist")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Clean Code")
        mock_wishlist_service.get_all_wishlists.assert_called_once()

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_get_wishlists_alternative_url_positive(self, mock_wishlist_service):
        # Positive: Alternative URL /wishlist returns 200 OK
        mock_wishlist_service.get_all_wishlists.return_value = []

        response = self.client.get("/wishlist")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        mock_wishlist_service.get_all_wishlists.assert_called_once()

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_get_wishlist_ids_positive(self, mock_wishlist_service):
        # Positive: /api/wishlist/ids returns 200 OK and list of string IDs
        mock_wishlist_service.get_wishlist_ids.return_value = ["w_1", "w_2"]

        response = self.client.get("/api/wishlist/ids")
        self.assertEqual(response.status_code, HTTPStatus.OK)
        data = json.loads(response.data)
        self.assertEqual(data["ids"], ["w_1", "w_2"])
        mock_wishlist_service.get_wishlist_ids.assert_called_once()

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_add_to_wishlist_success_positive(self, mock_wishlist_service):
        # Positive: Valid book JSON returns 201 Created and response message
        mock_wishlist_service.add_to_wishlist.return_value = {
            "id": "w_10",
            "title": "Pragmatic Programmer"
        }

        payload = {"id": "w_10", "title": "Pragmatic Programmer"}
        response = self.client.post(
            "/api/wishlist",
            data=json.dumps(payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

        data = json.loads(response.data)
        self.assertIn("data", data)
        self.assertEqual(data["data"]["title"], "Pragmatic Programmer")
        mock_wishlist_service.add_to_wishlist.assert_called_once_with(payload)

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_remove_from_wishlist_success_positive(self, mock_wishlist_service):
        # Positive: Valid book deletion returns 200 OK
        mock_wishlist_service.remove_from_wishlist.return_value = True

        response = self.client.delete("/api/wishlist/w_10")
        self.assertEqual(response.status_code, HTTPStatus.OK)

        data = json.loads(response.data)
        self.assertEqual(data["message"], "Berhasil dihapus dari wishlist.")
        mock_wishlist_service.remove_from_wishlist.assert_called_once_with("w_10")

    def test_add_to_wishlist_missing_body_negative(self):
        # Negative: Missing or non-JSON request body returns 400 Bad Request
        response = self.client.post("/api/wishlist", data="")
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_add_to_wishlist_validation_error_negative(self, mock_wishlist_service):
        # Negative: Domain validation failure returns 400 Bad Request
        mock_wishlist_service.add_to_wishlist.side_effect = DomainValidationError("Judul buku wajib diisi.")

        response = self.client.post(
            "/api/wishlist",
            data=json.dumps({"id": "w_1", "title": ""}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)

        data = json.loads(response.data)
        self.assertEqual(data["error"], "Judul buku wajib diisi.")

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_add_to_wishlist_server_error_negative(self, mock_wishlist_service):
        # Negative: Unexpected internal service error returns 500 Internal Server Error
        mock_wishlist_service.add_to_wishlist.side_effect = RuntimeError("Database connection dropped")

        response = self.client.post(
            "/api/wishlist",
            data=json.dumps({"id": "w_1", "title": "Clean Code"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

        data = json.loads(response.data)
        self.assertIn("error", data)

    @patch("app.wishlist.routes.wishlist_service", autospec=True)
    def test_remove_from_wishlist_not_found_negative(self, mock_wishlist_service):
        # Negative: Deleting non-existent item returns 404 Not Found
        mock_wishlist_service.remove_from_wishlist.return_value = False

        response = self.client.delete("/api/wishlist/not_found_id")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

        data = json.loads(response.data)
        self.assertEqual(data["error"], "Buku tidak ditemukan di wishlist.")
        mock_wishlist_service.remove_from_wishlist.assert_called_once_with("not_found_id")

    def test_wishlist_method_not_allowed_negative(self):
        # Negative: Unsupported HTTP method returns 405 Method Not Allowed
        response = self.client.put("/api/wishlist")
        self.assertEqual(response.status_code, HTTPStatus.METHOD_NOT_ALLOWED)


if __name__ == "__main__":
    unittest.main()
