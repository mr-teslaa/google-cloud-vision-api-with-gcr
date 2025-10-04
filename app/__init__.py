import logging
from flask import Flask, jsonify
from flask_restx import Api
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.exceptions import RequestEntityTooLarge
from .config import Config
from .routes import ns as ocr_namespace
from .utils.error_handler import register_error_handlers
from .schemas.response import error_response


def create_app():
    # Validate Google credentials at startup
    Config.validate_credentials()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
    )

    app.logger.info("App starting up...")

    # Rate limiting
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["5 per minute"],  # 5 requests per minute per IP
        storage_uri="memory://",
        headers_enabled=True,
    )
    limiter.init_app(app)

    # Create API with docs
    api = Api(
        app,
        version="1.0",
        title="FLEXBONE AI - CloudVision OCR API Assignment",
        description="Extract text from JPEG images using Google Cloud Vision API",
        doc="/docs",  # Swagger UI
    )

    # Register OCR namespace
    api.add_namespace(ocr_namespace, path="/api")

    # Register error handlers
    register_error_handlers(app)

    return app
