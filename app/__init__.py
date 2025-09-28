import os
from flask import Flask
from .config import Config
from .routes import register_routes
from .utils.error_handler import register_error_handlers


def create_app():
    # Verify that the Google application credentials environment variable is set
    Config.validate_credentials()

    app = Flask(__name__)
    app.config.from_object(Config)

    # Register routes
    register_routes(app)

    # Register global error handlers
    register_error_handlers(app)

    return app
