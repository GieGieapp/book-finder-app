import unittest
from unittest.mock import MagicMock, create_autospec

from core.constants import DEFAULT_UNKNOWN_AUTHOR
from core.errors import DomainValidationError
from app.wishlist.models import WishlistItem
from app.wishlist.schemas import WishlistItemSchema, WishlistItemDTO
from app.wishlist.service import WishlistService
from app.wishlist.repository import MongoWishlistRepository


class TestWishlistModelsAndSchemas(unittest.TestCase):
    def test_wishlist_model_creation_positive(self):
        # Positive: Verify domain entity properties and dictionary representation
        item = WishlistItem(id="w_1", title="Refactoring", rating=4.8)
        self.assertEqual(item.id, "w_1")
        self.assertEqual(item.title, "Refactoring")
        self.assertEqual(item.rating, 4.8)
        self.assertEqual(item.to_dict()["title"], "Refactoring")

    def test_wishlist_schema_contract_positive(self):
        # Positive: Verify response schema and compatibility DTO
        schema = WishlistItemSchema(id="s_1", title="Patterns")
        self.assertEqual(schema.id, "s_1")
        self.assertEqual(schema.to_dict()["title"], "Patterns")

        dto = WishlistItemDTO(id="dto_1", title="Patterns")
        self.assertEqual(dto.id, "dto_1")


class TestWishlistService(unittest.TestCase):
    def test_add_to_wishlist_success_positive(self):
        # Positive: Valid payload is parsed into entity, saved via repository, and returns schema
        mock_repo = create_autospec(MongoWishlistRepository)
        service = WishlistService(repository=mock_repo)

        payload = {
            "id": "book_101",
            "title": "Clean Architecture",
            "authors": ["Robert C. Martin"],
            "rating": 4.9
        }
        result = service.add_to_wishlist(payload)

        self.assertEqual(result["id"], "book_101")
        self.assertEqual(result["title"], "Clean Architecture")
        mock_repo.upsert.assert_called_once()

    def test_add_to_wishlist_with_default_fallbacks_positive(self):
        # Positive: Missing optional fields populate with defined defaults
        mock_repo = create_autospec(MongoWishlistRepository)
        service = WishlistService(repository=mock_repo)

        payload = {"id": "book_defaults", "title": "Minimal Book"}
        result = service.add_to_wishlist(payload)

        self.assertEqual(result["id"], "book_defaults")
        self.assertEqual(result["authors"], [DEFAULT_UNKNOWN_AUTHOR])
        self.assertEqual(result["rating"], 0.0)
        mock_repo.upsert.assert_called_once()

    def test_get_all_wishlists_success_positive(self):
        # Positive: Retrieves entities from repository and maps to schema list
        mock_repo = create_autospec(MongoWishlistRepository)
        mock_repo.find_all.return_value = [
            WishlistItem(id="1", title="Book One"),
            WishlistItem(id="2", title="Book Two")
        ]

        service = WishlistService(repository=mock_repo)
        items = service.get_all_wishlists()

        self.assertEqual(len(items), 2)
        self.assertEqual(items[0]["id"], "1")
        self.assertEqual(items[1]["id"], "2")
        mock_repo.find_all.assert_called_once()

    def test_get_all_wishlists_empty_positive(self):
        # Positive: Returns empty list when repository returns no items
        mock_repo = create_autospec(MongoWishlistRepository)
        mock_repo.find_all.return_value = []

        service = WishlistService(repository=mock_repo)
        items = service.get_all_wishlists()

        self.assertEqual(items, [])
        mock_repo.find_all.assert_called_once()

    def test_remove_from_wishlist_success_positive(self):
        # Positive: Deletion succeeds when repository returns True
        mock_repo = create_autospec(MongoWishlistRepository)
        mock_repo.delete_by_id.return_value = True

        service = WishlistService(repository=mock_repo)
        self.assertTrue(service.remove_from_wishlist("valid_id"))
        mock_repo.delete_by_id.assert_called_once_with("valid_id")

    def test_add_to_wishlist_missing_id_negative(self):
        # Negative: Raises DomainValidationError when book id is missing or whitespace
        mock_repo = create_autospec(MongoWishlistRepository)
        service = WishlistService(repository=mock_repo)

        with self.assertRaises(DomainValidationError):
            service.add_to_wishlist({"id": "", "title": "Some Title"})

        with self.assertRaises(DomainValidationError):
            service.add_to_wishlist({"id": "   ", "title": "Some Title"})

        mock_repo.upsert.assert_not_called()

    def test_add_to_wishlist_missing_title_negative(self):
        # Negative: Raises DomainValidationError when book title is missing or whitespace
        mock_repo = create_autospec(MongoWishlistRepository)
        service = WishlistService(repository=mock_repo)

        with self.assertRaises(DomainValidationError):
            service.add_to_wishlist({"id": "valid_id", "title": ""})

        with self.assertRaises(DomainValidationError):
            service.add_to_wishlist({"id": "valid_id", "title": "   "})

        mock_repo.upsert.assert_not_called()

    def test_add_to_wishlist_non_dict_payload_negative(self):
        # Negative: Raises DomainValidationError when input is not a dictionary
        mock_repo = create_autospec(MongoWishlistRepository)
        service = WishlistService(repository=mock_repo)

        with self.assertRaises(DomainValidationError):
            service.add_to_wishlist("string_payload")

        with self.assertRaises(DomainValidationError):
            service.add_to_wishlist(["list_payload"])

        mock_repo.upsert.assert_not_called()

    def test_remove_from_wishlist_empty_id_negative(self):
        # Negative: Returns False immediately without calling repository when ID is blank
        mock_repo = create_autospec(MongoWishlistRepository)
        service = WishlistService(repository=mock_repo)

        self.assertFalse(service.remove_from_wishlist(""))
        self.assertFalse(service.remove_from_wishlist("   "))
        mock_repo.delete_by_id.assert_not_called()

    def test_remove_from_wishlist_not_found_negative(self):
        # Negative: Returns False when repository fails to find and delete item
        mock_repo = create_autospec(MongoWishlistRepository)
        mock_repo.delete_by_id.return_value = False

        service = WishlistService(repository=mock_repo)
        self.assertFalse(service.remove_from_wishlist("non_existent_id"))
        mock_repo.delete_by_id.assert_called_once_with("non_existent_id")


class TestMongoWishlistRepository(unittest.TestCase):
    def setUp(self):
        self.mock_db = MagicMock()
        self.mock_collection = MagicMock()
        self.mock_db.__getitem__.return_value = self.mock_collection
        self.repo = MongoWishlistRepository(db=self.mock_db)

    def test_repository_upsert_positive(self):
        # Positive: Executes update_one with upsert flag
        item = WishlistItem(id="w1", title="Microservices")
        self.repo.upsert(item)

        self.mock_collection.update_one.assert_called_once_with(
            {"id": "w1"},
            {"$set": item.to_dict()},
            upsert=True
        )

    def test_repository_find_all_positive(self):
        # Positive: Queries collection and transforms cursor documents into entities
        self.mock_collection.find.return_value = [
            {"id": "w1", "title": "Book 1", "rating": 4.5},
            {"id": "w2", "title": "Book 2", "rating": 5.0}
        ]

        items = self.repo.find_all()
        self.assertEqual(len(items), 2)
        self.assertEqual(items[0].id, "w1")
        self.assertEqual(items[1].id, "w2")

    def test_repository_delete_by_id_positive(self):
        # Positive: Returns True when document is successfully deleted
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        self.mock_collection.delete_one.return_value = mock_result

        self.assertTrue(self.repo.delete_by_id("w1"))
        self.mock_collection.delete_one.assert_called_once_with({"id": "w1"})

    def test_repository_delete_by_id_not_found_negative(self):
        # Negative: Returns False when document to delete does not exist
        mock_result = MagicMock()
        mock_result.deleted_count = 0
        self.mock_collection.delete_one.return_value = mock_result

        self.assertFalse(self.repo.delete_by_id("non_existent"))
        self.mock_collection.delete_one.assert_called_once_with({"id": "non_existent"})

    def test_repository_delete_by_id_empty_negative(self):
        # Negative: Returns False when ID is empty string or None without calling database
        self.assertFalse(self.repo.delete_by_id(""))
        self.assertFalse(self.repo.delete_by_id("   "))
        self.mock_collection.delete_one.assert_not_called()

    def test_repository_document_mapping_failure_negative(self):
        # Negative: Gracefully ignores invalid or corrupt database records
        bad_doc = {"id": "corrupt", "rating": "invalid_number"}
        self.mock_collection.find.return_value = [
            {"id": "good_1", "title": "Good Book"},
            bad_doc
        ]

        items = self.repo.find_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0].id, "good_1")


if __name__ == "__main__":
    unittest.main()
