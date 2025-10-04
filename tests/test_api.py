import io
import pytest
from unittest.mock import patch


# ---------------------------
# Single image /extract-text
# ---------------------------
def test_extract_text_success(client):
    sample_image = io.BytesIO(b"\xff\xd8\xff\xdb\x00C\x00")
    sample_image.name = "test.jpg"

    with (
        patch("app.services.ocr_service.OCRService.extract_text") as mock_ocr,
        patch("app.services.ocr_service.OCRService.extract_metadata") as mock_meta,
    ):
        mock_ocr.return_value = {
            "text": "Hello World",
            "confidence": 0.95,
            "processing_time_ms": 50,
        }
        mock_meta.return_value = {
            "format": "JPEG",
            "mode": "RGB",
            "width": 100,
            "height": 100,
        }

        response = client.post(
            "/api/extract-text",
            data={"image": (sample_image, "test.jpg")},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is True
        assert data["text"] == "Hello World"
        assert "metadata" in data
        assert set(data["metadata"].keys()) == {"format", "mode", "width", "height"}


def test_no_file_uploaded(client):
    response = client.post(
        "/api/extract-text", data={}, content_type="multipart/form-data"
    )
    data = response.get_json()
    assert response.status_code == 400
    assert data["success"] is False


def test_empty_file(client):
    empty_file = io.BytesIO(b"")
    empty_file.name = "empty.jpg"
    response = client.post(
        "/api/extract-text",
        data={"image": (empty_file, "empty.jpg")},
        content_type="multipart/form-data",
    )
    data = response.get_json()
    assert response.status_code == 400
    assert "empty" in data["error"].lower()


def test_wrong_extension(client):
    fake_file = io.BytesIO(b"test")
    fake_file.name = "file.txt"
    response = client.post(
        "/api/extract-text",
        data={"image": (fake_file, "file.txt")},
        content_type="multipart/form-data",
    )
    data = response.get_json()
    assert response.status_code == 400
    assert "invalid file type" in data["error"].lower()


def test_wrong_mime_type(client):
    fake_file = io.BytesIO(b"test")
    fake_file.name = "file.jpg"
    response = client.post(
        "/api/extract-text",
        data={"image": (fake_file, "file.jpg")},
        content_type="application/json",  # Wrong content type
    )
    data = response.get_json()
    assert response.status_code == 415
    assert "invalid request type" in data["error"].lower()


# ---------------------------
# Batch upload /extract-text-batch
# ---------------------------
def test_extract_text_batch_success(client):
    img1 = io.BytesIO(b"\xff\xd8\xff\xdb\x00C\x00")
    img1.name = "image1.jpg"
    img2 = io.BytesIO(b"\xff\xd8\xff\xdb\x00D\x00")
    img2.name = "image2.png"

    with (
        patch("app.services.ocr_service.OCRService.extract_text") as mock_ocr,
        patch("app.services.ocr_service.OCRService.extract_metadata") as mock_meta,
    ):
        mock_ocr.side_effect = [
            {"text": "Hello", "confidence": 0.9, "processing_time_ms": 10},
            {"text": "World", "confidence": 0.8, "processing_time_ms": 12},
        ]
        mock_meta.side_effect = [
            {"format": "JPEG", "mode": "RGB", "width": 50, "height": 50},
            {"format": "PNG", "mode": "RGB", "width": 60, "height": 60},
        ]

        response = client.post(
            "/api/extract-text-batch",
            data={"image": [(img1, "image1.jpg"), (img2, "image2.png")]},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        assert response.status_code == 200
        assert data["success"] is True
        results = data["results"]
        assert len(results) == 2
        for r in results:
            assert "filename" in r
            assert "success" in r
            assert r["success"] is True
            assert "metadata" in r
            assert set(r["metadata"].keys()) == {"format", "mode", "width", "height"}


def test_extract_text_batch_invalid_file(client):
    img1 = io.BytesIO(b"test")
    img1.name = "badfile.exe"
    response = client.post(
        "/api/extract-text-batch",
        data={"image": [img1]},
        content_type="multipart/form-data",
    )
    data = response.get_json()
    assert response.status_code == 200
    results = data["results"]
    assert len(results) == 1
    assert results[0]["success"] is False
    assert "invalid file type" in results[0]["error"].lower()


# ---------------------------
# Health check
# ---------------------------
def test_health_check(client):
    response = client.get("/api/health")
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
            "/api/extract-text",
            data={"image": (sample_image, "test.jpg")},
            content_type="multipart/form-data",
        )
        data = response.get_json()
        assert response.status_code == 500
        assert "simulated vision api error" in data["error"].lower()
