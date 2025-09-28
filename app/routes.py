from flask import request, jsonify, Response
from .services.ocr_service import OCRService
from .utils.file_utils import allowed_file, get_secure_filename
from .schemas.response import success_response, error_response


def register_routes(app):
    @app.route("/extract-text", methods=["POST"])
    def extract_text():
        # Ensure correct content type
        if not request.content_type.startswith("multipart/form-data"):
            return error_response(
                "Invalid request type. Must be multipart/form-data", 415
            )

        if "image" not in request.files:
            return error_response("No image file provided in the request", 400)

        file = request.files["image"]

        # Check if file is selected
        if file.filename == "":
            return error_response("No file selected", 400)

        # Validate file extension
        if not allowed_file(file.filename):
            return error_response(
                "Invalid file type. Only JPG/JPEG files are allowed.", 400
            )

        # Validate MIME type
        if file.mimetype not in ["image/jpeg", "image/jpg"]:
            return error_response(
                f"Invalid MIME type: {file.mimetype}. Only JPEG images are allowed.",
                400,
            )

        # Validate file is not empty
        content = file.read()
        if not content or len(content) == 0:
            return error_response("Uploaded file is empty or unreadable.", 400)

        filename = get_secure_filename(file.filename)

        # Process OCR
        try:
            ocr = OCRService()
            result = ocr.extract_text(content)
            return success_response(result)
        except ValueError as ve:
            return error_response(str(ve), 400)
        except RuntimeError as re:
            return error_response(str(re), 500)
        except Exception as e:
            return error_response(f"Unexpected error: {str(e)}", 500)

    @app.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "healthy"}), 200
