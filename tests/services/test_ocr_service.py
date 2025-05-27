"""Tests for the OCR service."""

import io
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from pill_checker.services.ocr import EasyOCRClient, get_ocr_client


class MockReader:
    """Mock EasyOCR reader implementation."""

    def readtext(self, image_bytes, detail=0):
        """Return simulated OCR results."""
        return ["Mock OCR text", "for testing", "purposes"]


@pytest.fixture
def mock_ocr_client():
    """Create a mock OCR client for testing."""
    client = MagicMock(spec=EasyOCRClient)
    client.languages = ["en"]
    client.reader = MockReader()

    # Mock the read_text method
    client.read_text.return_value = "Mock OCR text for testing purposes"

    # Mock preprocessing methods
    client.preprocess_grayscale = MagicMock(side_effect=lambda img: img.convert("L"))
    client.preprocess_contrast = MagicMock(side_effect=lambda img: img)
    client.preprocess_sharpness = MagicMock(side_effect=lambda img: img)
    client.preprocess_denoise = MagicMock(side_effect=lambda img: img)
    client.preprocess_threshold = MagicMock(side_effect=lambda img: img)
    client.preprocess_resize = MagicMock(side_effect=lambda img: img.resize((100, 100)))
    client.preprocess_crop = MagicMock(side_effect=lambda img: img.crop((10, 10, 40, 40)))
    client.preprocess_image = MagicMock(side_effect=lambda img: img)

    return client


@pytest.fixture
def test_image():
    """Create a test PIL image."""
    return Image.new("RGB", (50, 50), (255, 255, 255))


class TestOCRService:
    """Test the OCR service with mocks."""

    def test_easyocr_client_initialization(self, mock_ocr_client):
        """Test that the EasyOCRClient initializes successfully."""
        assert mock_ocr_client is not None
        assert mock_ocr_client.reader is not None
        assert mock_ocr_client.languages == ["en"]

    def test_read_text_function(self, mock_ocr_client, test_image):
        """Test the read_text function with a mock image."""
        # Prepare image data
        image_bytes = io.BytesIO()
        test_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        result = mock_ocr_client.read_text(image_bytes)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Mock OCR text" in result
        mock_ocr_client.read_text.assert_called_once()

    def test_preprocess_grayscale(self, test_image):
        """Test grayscale conversion."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_grayscale(test_image)
        assert result.mode == "L"

    def test_preprocess_contrast(self, test_image):
        """Test contrast enhancement."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_contrast(test_image)
        assert isinstance(result, Image.Image)

    def test_preprocess_sharpness(self, test_image):
        """Test sharpness enhancement."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_sharpness(test_image)
        assert isinstance(result, Image.Image)

    def test_preprocess_denoise(self, test_image):
        """Test denoise filter."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_denoise(test_image)
        assert isinstance(result, Image.Image)

    def test_preprocess_threshold(self, test_image):
        """Test threshold filter."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_threshold(test_image)
        # Thresholding should result in values of only 0 and 255
        pixels = list(result.getdata())
        assert all(p in (0, 255) for p in pixels)

    def test_preprocess_resize(self, test_image):
        """Test image resizing."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_resize(test_image)
        assert result.size == (100, 100)  # 50 * 2 = 100

    def test_preprocess_crop(self, test_image):
        """Test image cropping."""
        client = EasyOCRClient.__new__(EasyOCRClient)
        result = client.preprocess_crop(test_image)
        assert result.size == (30, 30)  # 50 - 10*2 = 30

    def test_get_ocr_client(self):
        """Test the get_ocr_client function."""
        # Reset the global client first
        import pill_checker.services.ocr as ocr_module

        original_client = ocr_module._ocr_client

        try:
            # Set to None to force creation
            ocr_module._ocr_client = None

            # Mock EasyOCRClient to track calls
            with patch("pill_checker.services.ocr.EasyOCRClient") as mock_client_class:
                mock_instance = MagicMock(spec=EasyOCRClient)
                mock_client_class.return_value = mock_instance

                # Call get_ocr_client
                client = get_ocr_client()

                # Verify it created a new client
                mock_client_class.assert_called_once()
                assert client == mock_instance

        finally:
            # Restore original client
            ocr_module._ocr_client = original_client
