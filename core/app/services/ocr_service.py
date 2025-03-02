"""OCR service for text recognition from images."""

import io
from PIL import Image
from typing import Optional, Union, BinaryIO


# Define an abstract OCR client interface
class OCRClient:
    """Base class for OCR clients."""

    def read_text(self, image_data: Union[bytes, BinaryIO]) -> str:
        """
        Extract text from image data.

        Args:
            image_data: Image data as bytes or file-like object

        Returns:
            Extracted text
        """
        raise NotImplementedError("Subclasses must implement read_text")


class EasyOCRClient(OCRClient):
    """OCR client using EasyOCR."""

    def __init__(self, languages=None):
        """Initialize EasyOCR client."""
        self.languages = languages or ["en"]
        self._reader = None

    @property
    def reader(self):
        """Lazy-load the EasyOCR reader."""
        if self._reader is None:
            import easyocr

            self._reader = easyocr.Reader(self.languages, gpu=True)
        return self._reader

    def read_text(self, image_data: Union[bytes, BinaryIO]) -> str:
        """Extract text using EasyOCR."""
        # Process image
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            image = Image.open(image_data)

        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")

        # Convert to bytes for EasyOCR
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Extract text
        results = self.reader.readtext(image_bytes.read(), detail=0)
        return " ".join(results)


# Global OCR client instance - can be replaced for testing
_ocr_client: Optional[OCRClient] = None


def get_ocr_client() -> OCRClient:
    """Get the current OCR client."""
    global _ocr_client
    if _ocr_client is None:
        _ocr_client = EasyOCRClient()
    return _ocr_client


def set_ocr_client(client: OCRClient) -> None:
    """Set a custom OCR client (useful for testing)."""
    global _ocr_client
    _ocr_client = client


def recognise(uploaded_file) -> str:
    """
    Recognize text from an uploaded file.

    Args:
        uploaded_file: Uploaded file data

    Returns:
        Extracted text
    """
    return get_ocr_client().read_text(uploaded_file)
