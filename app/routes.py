from flask import request
from flask_restx import Namespace, Resource, reqparse
from .services.ocr_service import OCRService
from .utils.file_utils import allowed_file, get_secure_filename
from .schemas.input import register_input_schemas
from .schemas.response import register_output_schemas, success_response, error_response

# Create namespace
ns = Namespace("OCR", description="OCR operations")

# Register models with namespace
OCRInputSchema = register_input_schemas(ns)
OCROutputSchema = register_output_schemas(ns)


# Parser for multipart/form-data
upload_parser = reqparse.RequestParser()
upload_parser.add_argument(
    "image",
    location="files",
    type="FileStorage",
    required=True,
    help="JPEG image file to extract text from",
)


@ns.route("/extract-text")
class ExtractText(Resource):
    @ns.expect(upload_parser)
    @ns.response(200, "Success", OCROutputSchema)
    @ns.response(400, "Bad Request")
    @ns.response(415, "Unsupported Media Type")
    @ns.response(500, "Internal Server Error")
    def post(self):
        """Extract text from uploaded JPG image"""
        if not request.content_type.startswith("multipart/form-data"):
            return error_response(
                "Invalid request type. Must be multipart/form-data", 415
            )

        if "image" not in request.files:
            return error_response("No image file provided in the request", 400)

        file = request.files["image"]

        if file.filename == "":
            return error_response("No file selected", 400)

        if not allowed_file(file.filename):
            return error_response(
                "Invalid file type. Only JPG/JPEG files are allowed.", 400
            )

        if file.mimetype not in ["image/jpeg", "image/jpg"]:
            return error_response(
                f"Invalid MIME type: {file.mimetype}. Only JPEG images are allowed.",
                400,
            )

        content = file.read()
        if not content or len(content) == 0:
            return error_response("Uploaded file is empty or unreadable.", 400)

        filename = get_secure_filename(file.filename)

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


@ns.route("/health")
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        return {"status": "healthy"}, 200
