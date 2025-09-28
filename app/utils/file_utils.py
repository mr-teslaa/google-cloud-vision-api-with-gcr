from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename: str) -> bool:
    """Check if file extension is allowed."""
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_EXTENSIONS"]
    )


def get_secure_filename(filename: str) -> str:
    return secure_filename(filename)
