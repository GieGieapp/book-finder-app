from http import HTTPStatus
from flask import jsonify


class DomainValidationError(Exception):
    """Raised when a business domain rule or invariant is violated"""
    pass


def register_error_handlers(app):
    """Registers standard HTTP error handlers on Flask application"""
    @app.errorhandler(DomainValidationError)
    def handle_validation(err):
        return jsonify({"error": str(err)}), HTTPStatus.BAD_REQUEST

    @app.errorhandler(404)
    def handle_not_found(err):
        return jsonify({"error": "Resource not found."}), HTTPStatus.NOT_FOUND

    @app.errorhandler(500)
    def handle_server_error(err):
        return jsonify({"error": "Internal server error."}), HTTPStatus.INTERNAL_SERVER_ERROR
