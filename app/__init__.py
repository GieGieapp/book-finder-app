from flask import Flask, jsonify
from core.config import get_config
from infrastructure.database import db_manager
from core.errors import register_error_handlers
from core.logger import setup_logging

from .views import view_bp
from .books import book_bp
from .wishlist import wishlist_bp


def create_app(config_class=None):
    """
    Application Factory Pattern
    Initializes core platform extensions, domain blueprints, and error handlers.
    """
    app = Flask(
        __name__,
        template_folder="views/templates",
        static_folder="views/static"
    )

    # 1. Configuration
    if config_class is None:
        config_class = get_config()
    app.config.from_object(config_class)

    # 2. Centralized Structured Logging
    setup_logging(app)

    # 3. Database Initialization
    db_manager.init_app(app)

    # 4. Global Error Handlers
    register_error_handlers(app)

    # 5. Domain Blueprints (Modular DDD)
    app.register_blueprint(view_bp)
    app.register_blueprint(book_bp)
    app.register_blueprint(wishlist_bp)

    # 6. Health Check Endpoint (Readiness & Liveness Probe)
    @app.route("/health", methods=["GET"])
    @app.route("/api/health", methods=["GET"])
    def health_check():
        is_healthy = db_manager.ping()
        return jsonify({
            "status": "healthy" if is_healthy else "degraded",
            "environment": app.config.get("ENV_NAME", "development"),
            "database": "connected" if is_healthy else "disconnected"
        }), 200

    return app
