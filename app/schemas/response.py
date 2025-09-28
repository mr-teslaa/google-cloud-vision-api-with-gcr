import json
from flask import Response


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
