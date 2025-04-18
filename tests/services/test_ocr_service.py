"""Tests for the OCR service."""

import io
from unittest.mock import patch

import pytest
from PIL import Image

from src.pill_checker.main import app
from src.pill_checker.services.ocr import EasyOCRClient

# Original client reference
_original_client = None


class MockReader:
    """Mock EasyOCR reader implementation."""

    def readtext(self, image_bytes, detail=0):
        """Return simulated OCR results."""
        return ["Mock OCR text", "for testing", "purposes"]


def setup_module(module):
    """Set up the module with a mocked OCR client."""
    global _original_client
    _original_client = app.services.ocr_service._ocr_client

    # Create a mock client
    mock_client = EasyOCRClient.__new__(EasyOCRClient)
    mock_client.languages = ["en"]
    mock_client.reader = MockReader()

    # Replace the real client with our mock
    app.services.ocr_service._ocr_client = mock_client


def teardown_module(module):
    """Restore the original OCR client."""
    global _original_client
    if _original_client:
        app.services.ocr_service._ocr_client = _original_client


@pytest.fixture
def mock_ocr_client():
    """Create a mock OCR client for testing."""
    client = EasyOCRClient.__new__(EasyOCRClient)
    client.languages = ["en"]
    client.reader = MockReader()

    # Save existing methods before we mock them
    original_preprocess_image = EasyOCRClient.preprocess_image

    # Mock the preprocessing method to avoid actual image processing
    def mock_preprocess(self, image):
        return image

    # Apply the mock
    EasyOCRClient.preprocess_image = mock_preprocess

    yield client

    # Restore original methods
    EasyOCRClient.preprocess_image = original_preprocess_image


@pytest.fixture
def test_image():
    """Create a test PIL image."""
    return Image.new("RGB", (50, 50), (255, 255, 255))


class TestOCRService:
    """Test the OCR service with mocks."""

    def test_easyocr_client_initialization(self, mock_ocr_client):
        """Test that the EasyOCRClient initializes successfully."""
        assert isinstance(mock_ocr_client, EasyOCRClient)
        assert mock_ocr_client.reader is not None
        assert mock_ocr_client.languages == ["en"]

    def test_read_text_function(self, mock_ocr_client, test_image):
        """Test the read_text function with a mock image."""
        # Prepare image data
        image_bytes = io.BytesIO()
        test_image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # Mock the preprocess_image method to return the original image
        with patch.object(mock_ocr_client, "preprocess_image", return_value=test_image):
            result = mock_ocr_client.read_text(image_bytes)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Mock OCR text" in result

    def test_preprocess_grayscale(self, mock_ocr_client, test_image):
        """Test grayscale conversion."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_grayscale(
            mock_ocr_client, test_image
        )
        assert result.mode == "L"

    def test_preprocess_contrast(self, mock_ocr_client, test_image):
        """Test contrast enhancement."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_contrast(
            mock_ocr_client, test_image
        )
        assert isinstance(result, Image.Image)

    def test_preprocess_sharpness(self, mock_ocr_client, test_image):
        """Test sharpness enhancement."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_sharpness(
            mock_ocr_client, test_image
        )
        assert isinstance(result, Image.Image)

    def test_preprocess_denoise(self, mock_ocr_client, test_image):
        """Test denoise filter."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_denoise(
            mock_ocr_client, test_image
        )
        assert isinstance(result, Image.Image)

    def test_preprocess_threshold(self, mock_ocr_client, test_image):
        """Test threshold filter."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_threshold(
            mock_ocr_client, test_image
        )
        # Thresholding should result in values of only 0 and 255
        pixels = list(result.getdata())
        assert all(p in (0, 255) for p in pixels)

    def test_preprocess_resize(self, mock_ocr_client, test_image):
        """Test image resizing."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_resize(
            mock_ocr_client, test_image
        )
        assert result.size == (100, 100)  # 50 * 2 = 100

    def test_preprocess_crop(self, mock_ocr_client, test_image):
        """Test image cropping."""
        # The real implementation
        result = app.services.ocr_service.EasyOCRClient.preprocess_crop(mock_ocr_client, test_image)
        assert result.size == (30, 30)  # 50 - 10*2 = 30

    def test_get_ocr_client(self):
        """Test the get_ocr_client function."""
        with patch("app.services.ocr_service.EasyOCRClient") as mock_client_class:
            # Reset the global client
            app.services.ocr_service._ocr_client = None

            # Call the function
            app.services.ocr_service.get_ocr_client()

            # Check that a new client was created
            mock_client_class.assert_called_once()

            # Reset the global client
            app.services.ocr_service._ocr_client = _original_client
