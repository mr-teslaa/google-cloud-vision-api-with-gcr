from flask import Flask
from flask_restx import Api
from .config import Config
from .routes import ns as ocr_namespace
from .utils.error_handler import register_error_handlers


def create_app():
    # Validate Google credentials at startup
    Config.validate_credentials()

    app = Flask(__name__)
    app.config.from_object(Config)

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
