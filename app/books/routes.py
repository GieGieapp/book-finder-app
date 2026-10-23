from http import HTTPStatus
from flask import Blueprint, request, jsonify
from .service import BookService

book_bp = Blueprint('book_bp', __name__)
book_service = BookService()


@book_bp.route('/search', methods=['GET'])
@book_bp.route('/api/search', methods=['GET'])
def search_books():
    """Searches book catalog via keyword query parameter with pagination support"""
    keyword = request.args.get('q', '').strip()
    page_param = request.args.get('page')
    if page_param:
        try:
            page = max(1, int(page_param))
            start_index = (page - 1) * 20
            books = book_service.search_books(keyword, start_index=start_index)
        except (ValueError, TypeError):
            books = book_service.search_books(keyword)
    else:
        books = book_service.search_books(keyword)
    return jsonify(books), HTTPStatus.OK
