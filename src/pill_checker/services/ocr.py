"""OCR service for text recognition from images."""

import io
from typing import BinaryIO, Union

from PIL import Image, ImageEnhance, ImageFilter


class EasyOCRClient:
    """OCR client using EasyOCR."""

    def __init__(self, languages=None):
        """Initialize EasyOCR reader immediately on startup."""
        self.languages = languages or ["en"]
        import easyocr

        self.reader = easyocr.Reader(self.languages)
        print("EasyOCR initialized and ready")

    def preprocess_grayscale(self, image: Image.Image) -> Image.Image:
        """Convert image to grayscale."""
        return image.convert("L")

    def preprocess_contrast(self, image: Image.Image, factor: float = 1.5) -> Image.Image:
        """Enhance image contrast."""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    def preprocess_sharpness(self, image: Image.Image, factor: float = 2.0) -> Image.Image:
        """Enhance image sharpness."""
        enhancer = ImageEnhance.Sharpness(image)
        return enhancer.enhance(factor)

    def preprocess_denoise(self, image: Image.Image) -> Image.Image:
        """Apply median filter to denoise image."""
        return image.filter(ImageFilter.MedianFilter(size=3))

    def preprocess_threshold(self, image: Image.Image, threshold: int = 128) -> Image.Image:
        """Convert image to binary using threshold."""
        grayscale = image.convert("L")
        return grayscale.point(lambda p: 255 if p > threshold else 0)

    def preprocess_resize(self, image: Image.Image, scale_factor: float = 2.0) -> Image.Image:
        """Resize image by a scale factor."""
        width, height = image.size
        new_size = (int(width * scale_factor), int(height * scale_factor))
        return image.resize(new_size, Image.LANCZOS)

    def preprocess_crop(self, image: Image.Image, border: int = 10) -> Image.Image:
        """Crop a fixed border from the image."""
        width, height = image.size
        return image.crop((border, border, width - border, height - border))

    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Chain all pre-processing steps and convert to RGB at the end."""
        image = self.preprocess_grayscale(image)
        image = self.preprocess_contrast(image)
        image = self.preprocess_sharpness(image)
        image = self.preprocess_denoise(image)
        image = self.preprocess_threshold(image)
        image = self.preprocess_resize(image)
        image = self.preprocess_crop(image)
        return image.convert("RGB")

    def read_text(self, image_data: Union[bytes, BinaryIO]) -> str:
        """Extract text using EasyOCR."""
        # Load image from bytes or file-like object
        if isinstance(image_data, bytes):
            image = Image.open(io.BytesIO(image_data))
        else:
            image = Image.open(image_data)

        # Preprocess image using the defined chain
        image = self.preprocess_image(image)

        # Convert preprocessed image to bytes for EasyOCR
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # Extract text
        results = self.reader.readtext(image_bytes.read(), detail=0)
        return " ".join(results)


_ocr_client = None


def get_ocr_client(languages=None):
    """Get or create the OCR client singleton."""
    global _ocr_client
    if _ocr_client is None:
        _ocr_client = EasyOCRClient(languages=languages)
    return _ocr_client
