from flask import jsonify


class DomainValidationError(Exception):
    """Custom exception untuk pelanggaran aturan bisnis domain"""
    pass


def register_error_handlers(app):
    @app.errorhandler(DomainValidationError)
    def handle_domain_validation(err):
        return jsonify({"error": str(err)}), 400

    @app.errorhandler(404)
    def handle_404(err):
        return jsonify({"error": "Resource yang diminta tidak ditemukan."}), 404

    @app.errorhandler(500)
    def handle_500(err):
        return jsonify({"error": "Terjadi kesalahan internal pada server."}), 500
