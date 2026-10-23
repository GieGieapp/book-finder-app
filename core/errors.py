from http import HTTPStatus
from typing import Optional
from flask import jsonify


class AppException(Exception):
    """Base application exception for all domain and system errors"""
    status_code: int = HTTPStatus.INTERNAL_SERVER_ERROR

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code


class DomainValidationError(AppException):
    """Raised when an entity or input violates domain business invariants"""
    status_code: int = HTTPStatus.BAD_REQUEST


class ResourceNotFoundError(AppException):
    """Raised when a requested domain entity is not found"""
    status_code: int = HTTPStatus.NOT_FOUND


def register_error_handlers(app):
    """Registers centralized HTTP error handlers on Flask application"""
    @app.errorhandler(AppException)
    def handle_app_exception(err: AppException):
        return jsonify({"error": err.message}), err.status_code

    @app.errorhandler(HTTPStatus.NOT_FOUND)
    def handle_not_found(_err):
        return jsonify({"error": "Resource not found."}), HTTPStatus.NOT_FOUND

    @app.errorhandler(HTTPStatus.INTERNAL_SERVER_ERROR)
    def handle_server_error(_err):
        return jsonify({"error": "Internal server error."}), HTTPStatus.INTERNAL_SERVER_ERROR
