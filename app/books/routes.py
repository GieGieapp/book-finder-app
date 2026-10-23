from http import HTTPStatus
from flask import Blueprint, request, jsonify
from .service import BookService

book_bp = Blueprint('book_bp', __name__)
book_service = BookService()


@book_bp.route('/search', methods=['GET'])
@book_bp.route('/api/search', methods=['GET'])
def search_books():
    """Searches book catalog via keyword query parameter"""
    keyword = request.args.get('q', '').strip()
    books = book_service.search_books(keyword)
    return jsonify(books), HTTPStatus.OK
