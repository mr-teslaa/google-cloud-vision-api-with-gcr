from flask import request, current_app
from flask_restx import Namespace, Resource, reqparse
from concurrent.futures import ThreadPoolExecutor, as_completed
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

batch_upload_parser = reqparse.RequestParser()
batch_upload_parser.add_argument(
    "image",
    location="files",
    type="FileStorage",
    required=True,
    action="append",  # ✅ allows multiple files in Swagger UI
    help="JPEG, PNG, GIF, or WEBP image files to extract text from",
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
        if (
            not request.content_type
            or "multipart/form-data" not in request.content_type
        ):
            return error_response(
                "Invalid request type. Must be multipart/form-data", 415
            )

        if "image" not in request.files:
            return error_response("No image file provided in the request", 400)

        file = request.files["image"]

        if file.filename == "":
            return error_response("No file selected", 400)

        ALLOWED_EXTENSIONS = current_app.config["ALLOWED_EXTENSIONS"]

        if not allowed_file(file.filename, ALLOWED_EXTENSIONS):
            return error_response(
                "Invalid file type. Only JPG/JPEG files are allowed.", 400
            )

        if file.mimetype not in [
            "image/jpeg",
            "image/jpg",
            "image/png",
            "image/gif",
            "image/webp",
        ]:
            return error_response(
                f"Invalid MIME type: {file.mimetype}. Only JPEG, PNG, and GIF images are allowed.",
                400,
            )

        content = file.read()
        if not content or len(content) == 0:
            return error_response("Uploaded file is empty or unreadable.", 400)

        filename = get_secure_filename(file.filename)

        try:
            ocr = OCRService()
            result = ocr.extract_text(content)
            metadata = ocr.extract_metadata(content)
            result["metadata"] = metadata
            return success_response(result)
        except ValueError as ve:
            return error_response(str(ve), 400)
        except RuntimeError as re:
            return error_response(str(re), 500)
        except Exception as e:
            return error_response(f"Unexpected error: {str(e)}", 500)


@ns.route("/extract-text-batch")
class ExtractTextBatch(Resource):
    @ns.expect(batch_upload_parser)
    def post(self):
        """Extract text from multiple uploaded images concurrently (max 10 threads)"""
        if not request.files or not request.files.getlist("image"):
            return error_response("No image files provided", 400)

        files = request.files.getlist("image")
        results = []
        ocr = OCRService()

        ALLOWED_EXTENSIONS = current_app.config["ALLOWED_EXTENSIONS"]

        def process_file(file, allowed_extensions=ALLOWED_EXTENSIONS):
            """Worker function for ThreadPoolExecutor"""
            if not allowed_file(file.filename, allowed_extensions):
                return {
                    "filename": file.filename,
                    "success": False,
                    "error": "Invalid file type.",
                }

            content = file.read()
            if not content:
                return {
                    "filename": file.filename,
                    "success": False,
                    "error": "Empty or unreadable file.",
                }

            try:
                result = ocr.extract_text(content)
                metadata = ocr.extract_metadata(content)
                result["metadata"] = metadata
                return {"filename": file.filename, "success": True, **result}
            except Exception as e:
                return {"filename": file.filename, "success": False, "error": str(e)}

        # Use ThreadPoolExecutor for concurrent processing
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {
                executor.submit(process_file, file): file.filename for file in files
            }
            for future in as_completed(futures):
                results.append(future.result())

        return success_response({"results": results})


@ns.route("/health")
class Health(Resource):
    def get(self):
        """Health check endpoint"""
        return {"status": "healthy"}, 200
