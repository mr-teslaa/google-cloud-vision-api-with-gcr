import io
import pytest
from unittest.mock import patch


# ---------------------------
# Happy path: valid JPEG image
# ---------------------------
def test_extract_text_success(client):
    # Use a small sample JPEG (can be any small valid bytes)
    sample_image = io.BytesIO(b"\xff\xd8\xff\xdb\x00C\x00")
    sample_image.name = "test.jpg"

    # Patch OCRService to avoid real Google Vision calls
    with patch("app.services.ocr_service.OCRService.extract_text") as mock_ocr:
        mock_ocr.return_value = {
            "text": "Hello World",
            "confidence": 0.99,
            "processing_time_ms": 50,
        }

        response = client.post(
            "/extract-text",
            data={"image": (sample_image, "test.jpg")},
            content_type="multipart/form-data",
        )

        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is True
        assert data["text"] == "Hello World"
        assert 0 <= data["confidence"] <= 1


# ---------------------------
# Edge cases / validation
# ---------------------------
def test_no_file_uploaded(client):
    response = client.post("/extract-text", data={}, content_type="multipart/form-data")
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False


def test_empty_file(client):
    empty_file = io.BytesIO(b"")
    empty_file.name = "empty.jpg"

    response = client.post(
        "/extract-text",
        data={"image": (empty_file, "empty.jpg")},
        content_type="multipart/form-data",
    )
    data = response.get_json()
    assert response.status_code == 400
    assert "empty" in data["error"].lower()


def test_wrong_extension(client):
    fake_file = io.BytesIO(b"test")
    fake_file.name = "file.png"

    response = client.post(
        "/extract-text",
        data={"image": (fake_file, "file.png")},
        content_type="multipart/form-data",
    )
    data = response.get_json()
    assert response.status_code == 400
    assert "invalid file type" in data["error"].lower()


def test_wrong_mime_type(client):
    fake_file = io.BytesIO(b"test")
    fake_file.name = "file.jpg"

    response = client.post(
        "/extract-text",
        data={"image": (fake_file, "file.jpg")},
        content_type="application/json",  # Wrong content type
    )
    data = response.get_json()
    assert response.status_code == 415
    assert "invalid request type" in data["error"].lower()


# ---------------------------
# Health check
# ---------------------------
def test_health_check(client):
    response = client.get("/health")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "healthy"


# ---------------------------
# OCRService error handling simulation
# ---------------------------
def test_ocr_service_runtime_error(client):
    sample_image = io.BytesIO(b"\xff\xd8\xff\xdb")
    sample_image.name = "test.jpg"

    with patch("app.services.ocr_service.OCRService.extract_text") as mock_ocr:
        mock_ocr.side_effect = RuntimeError("Simulated Vision API error")
        response = client.post(
            "/extract-text",
            data={"image": (sample_image, "test.jpg")},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        assert response.status_code == 500
        assert "simulated vision api error" in data["error"].lower()
