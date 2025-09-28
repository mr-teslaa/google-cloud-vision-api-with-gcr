from flask import jsonify


def register_error_handlers(app):
    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({"success": False, "error": "File too large"}), 413

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"success": False, "error": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def internal_error(e):
        return jsonify({"success": False, "error": "Internal server error"}), 500
