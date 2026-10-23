from http import HTTPStatus
from flask import Blueprint, request, jsonify
from core.errors import DomainValidationError
from core.logger import get_logger
from .service import WishlistService

logger = get_logger(__name__)
wishlist_bp = Blueprint('wishlist_bp', __name__)
wishlist_service = WishlistService()


@wishlist_bp.route('/wishlist', methods=['GET'])
@wishlist_bp.route('/api/wishlist', methods=['GET'])
def get_wishlists():
    """Retrieves book items in the wishlist with pagination support"""
    page_param = request.args.get('page')
    limit_param = request.args.get('limit')
    if page_param or limit_param:
        try:
            page = max(1, int(page_param or 1))
            limit = max(1, min(100, int(limit_param or 20)))
            skip = (page - 1) * limit
            items = wishlist_service.get_all_wishlists(limit=limit, skip=skip)
        except (ValueError, TypeError):
            items = wishlist_service.get_all_wishlists()
    else:
        items = wishlist_service.get_all_wishlists()
    return jsonify(items), HTTPStatus.OK


@wishlist_bp.route('/wishlist/count', methods=['GET'])
@wishlist_bp.route('/api/wishlist/count', methods=['GET'])
def get_wishlist_count():
    """Returns the total number of books saved in the wishlist"""
    count = wishlist_service.count_all_wishlists()
    return jsonify({"count": count}), HTTPStatus.OK


@wishlist_bp.route('/wishlist/ids', methods=['GET'])
@wishlist_bp.route('/api/wishlist/ids', methods=['GET'])
def get_wishlist_ids():
    """Returns array of all wishlist book IDs for client-side state checking"""
    ids = wishlist_service.get_wishlist_ids()
    return jsonify({"ids": ids}), HTTPStatus.OK


@wishlist_bp.route('/wishlist', methods=['POST'])
@wishlist_bp.route('/api/wishlist', methods=['POST'])
def add_to_wishlist():
    """Adds a new book to the wishlist"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body harus berupa JSON yang valid."}), HTTPStatus.BAD_REQUEST

    try:
        saved_item = wishlist_service.add_to_wishlist(data)
        return jsonify({"message": "Berhasil ditambahkan", "data": saved_item}), HTTPStatus.CREATED
    except DomainValidationError as exc:
        logger.warning("Wishlist validation failed: %s", exc)
        return jsonify({"error": str(exc)}), HTTPStatus.BAD_REQUEST
    except Exception as exc:
        logger.error("Internal server error while saving wishlist: %s", exc, exc_info=True)
        return jsonify({"error": "Terjadi kesalahan server saat menyimpan wishlist."}), HTTPStatus.INTERNAL_SERVER_ERROR


@wishlist_bp.route('/wishlist/<book_id>', methods=['DELETE'])
@wishlist_bp.route('/api/wishlist/<book_id>', methods=['DELETE'])
def remove_from_wishlist(book_id):
    """Removes a book from the wishlist by ID"""
    deleted = wishlist_service.remove_from_wishlist(book_id)
    if deleted:
        return jsonify({"message": "Berhasil dihapus dari wishlist."}), HTTPStatus.OK
    return jsonify({"error": "Buku tidak ditemukan di wishlist."}), HTTPStatus.NOT_FOUND
