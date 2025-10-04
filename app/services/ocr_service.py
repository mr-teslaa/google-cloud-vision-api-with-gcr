import time, re
from io import BytesIO
from PIL import Image
from flask import current_app
from google.cloud import vision
from google.api_core.exceptions import GoogleAPIError


class OCRService:
    def __init__(self):
        if "GOOGLE_CREDENTIALS" not in current_app.config:
            raise RuntimeError("Google credentials not configured")
        self.client = vision.ImageAnnotatorClient()

    def clean_text(self, text: str) -> str:
        """Normalize whitespace, remove artifacts."""
        if not text:
            return ""
        # Replace multiple spaces/newlines with single space or newline
        text = re.sub(r"\s+", " ", text)
        text = text.strip()
        return text

    def extract_metadata(self, content: bytes) -> dict:
        try:
            with Image.open(BytesIO(content)) as img:
                return {
                    "format": img.format,
                    "mode": img.mode,
                    "width": img.width,
                    "height": img.height,
                }
        except Exception:
            return {}

    def extract_text(self, content: bytes) -> dict:
        """Extract text from image bytes with robust error handling."""
        start_time = time.time()

        if not content or len(content) == 0:
            raise ValueError("Uploaded file is empty or unreadable.")

        try:
            image = vision.Image(content=content)
            response = self.client.document_text_detection(image=image)
        except GoogleAPIError as e:
            raise RuntimeError(f"Google Vision API error: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"OCR failed: {str(e)}")

        processing_time_ms = int((time.time() - start_time) * 1000)

        if response.error.message:
            raise RuntimeError(f"Vision API error: {response.error.message}")

        text = (
            response.full_text_annotation.text
            if response.full_text_annotation.text
            else ""
        )

        # Clean up text
        text = self.clean_text(text)

        total_conf, count = 0.0, 0
        for page in response.full_text_annotation.pages:
            for block in page.blocks:
                for paragraph in block.paragraphs:
                    for word in paragraph.words:
                        if word.confidence:
                            total_conf += word.confidence
                            count += 1

        confidence = round(total_conf / count, 2) if count > 0 else 0.0

        return {
            "text": text,
            "confidence": confidence,
            "processing_time_ms": processing_time_ms,
        }
