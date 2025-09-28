import json
from flask import Response
from flask_restx import fields


def register_output_schemas(api):
    OCROutputSchema = api.model(
        "OCROutput",
        {
            "success": fields.Boolean(required=True, description="Request status"),
            "text": fields.String(description="Extracted text from image"),
            "confidence": fields.Float(description="Average OCR confidence"),
            "processing_time_ms": fields.Integer(description="Processing time in ms"),
        },
    )
    return OCROutputSchema


def success_response(data: dict, status: int = 200) -> Response:
    return Response(
        json.dumps({"success": True, **data}, ensure_ascii=False),
        status=status,
        mimetype="application/json; charset=utf-8",
    )


def error_response(message: str, status: int) -> Response:
    return Response(
        json.dumps({"success": False, "error": message}, ensure_ascii=False),
        status=status,
        mimetype="application/json; charset=utf-8",
    )
