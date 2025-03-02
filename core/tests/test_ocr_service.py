"""Tests for the OCR service with real easyocr implementation."""

import io
import os
import pytest
from pathlib import Path

from app.services.ocr_service import (
    EasyOCRClient,
    get_ocr_client,
    set_ocr_client,
    recognise,
)

# Mark all tests in this module with the 'ocr' marker
pytestmark = [
    # Skip these tests in CI environments or when fast testing is needed
    pytest.mark.skipif(
        os.environ.get("SKIP_REAL_OCR_TESTS", "False").lower() in ("true", "1", "t"),
        reason="Real OCR tests are slow and require easyocr",
    ),
    # Mark as OCR tests so they can be selectively included/excluded
    pytest.mark.ocr,
]

# Module-level setup for the OCR client to avoid multiple initializations
# This makes tests run much faster since we only initialize easyocr once
_original_client = None


def setup_module(module):
    """Set up the module by initializing the OCR client once."""
    global _original_client
    _original_client = get_ocr_client()
    print("Setting up real EasyOCR client - this may take a moment during first run...")

    # Create test images directory if it doesn't exist
    test_images_dir = Path(__file__).parent / "test_images"
    test_images_dir.mkdir(exist_ok=True)

    # Check if we have test images, if not create them
    image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
    if not image_files:
        try:
            # Try to import and use create_test_image script
            from test_utils.test_create_test_image import create_multiple_test_images

            created_images = create_multiple_test_images(count=2)
            print(f"Created {len(created_images)} test images for OCR testing")
        except ImportError as e:
            print(f"Warning: No test images found and couldn't import create_test_image: {e}")


def teardown_module(module):
    """Restore the original OCR client."""
    global _original_client
    if _original_client:
        set_ocr_client(_original_client)
        print("Restored original OCR client")


@pytest.fixture(scope="module")
def ocr_client():
    """Create a real OCR client for testing."""
    # Create a real client for the test
    client = EasyOCRClient()
    set_ocr_client(client)

    yield client

    # No need to restore here as it's done in teardown_module


@pytest.fixture
def test_images_dir():
    """Get the directory containing test images."""
    # Check if we have a test_images directory
    base_dir = Path(__file__).parent
    test_images_path = base_dir / "test_images"

    if not test_images_path.exists() or not any(test_images_path.iterdir()):
        pytest.skip("Test images directory not found or empty")

    return test_images_path


class TestOCRService:
    """Test the OCR service with real implementation."""

    def test_easyocr_client_initialization(self, ocr_client):
        """Test that the EasyOCRClient initializes successfully."""
        assert isinstance(ocr_client, EasyOCRClient)
        # We don't access reader directly as it loads models which is slow
        assert ocr_client is not None

    @pytest.mark.skipif(not os.path.exists("tests/test_images"), reason="Test images not available")
    def test_ocr_with_test_images(self, ocr_client, test_images_dir):
        """Test OCR with the pre-generated test images."""
        # Look for PNG or JPG images in the test_images directory
        image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))

        if not image_files:
            pytest.skip("No test images found in the test_images directory")

        # Test with each image found
        for image_file in image_files:
            with open(image_file, "rb") as f:
                image_data = f.read()

            # Process the image
            result = ocr_client.read_text(io.BytesIO(image_data))

            # Check that the result is a string
            assert isinstance(result, str)
            # Log the detected text for verification
            print(f"Image: {image_file.name}, Detected text: {result}")

            # Define expected keywords based on the image filename
            if "prescription" in image_file.name.lower():
                # For prescription images we expect medication related terms
                expected_keywords = [
                    "TABLET",
                    "DAILY",
                    "Ibuprofen",
                    "MEDICATION",
                    "CHILDREN",
                    "Store",
                ]
            else:
                # For other test images, use generic expectations
                expected_keywords = ["test", "sample", "text", "image"]

            # Check that some keywords are found (allowing for OCR errors)
            found_keywords = [
                keyword for keyword in expected_keywords if keyword.lower() in result.lower()
            ]

            # We should find at least some of the expected keywords
            assert (
                len(found_keywords) > 0
            ), f"No expected keywords found in OCR result for {image_file.name}: '{result}'"

            # A more comprehensive check on the extracted information
            extracted_info = {
                "has_dosage": any(x in result.lower() for x in ["mg", "200"]),
                "has_instruction": any(x in result.upper() for x in ["TABLET", "DAILY", "TAKE"]),
                "has_storage": "store" in result.lower() or "temperature" in result.lower(),
            }

            # Make sure we captured some of the key information
            assert (
                sum(extracted_info.values()) > 0
            ), f"Failed to extract key information from {image_file.name}: {extracted_info}"

    def test_recognise_function(self, ocr_client, test_images_dir):
        """Test the higher-level recognise function with a test image."""
        # Skip if no test images
        image_files = list(test_images_dir.glob("*.png")) + list(test_images_dir.glob("*.jpg"))
        if not image_files:
            pytest.skip("No test images found in the test_images directory")

        # Use the first image found
        with open(image_files[0], "rb") as f:
            image_data = io.BytesIO(f.read())

        # Test the recognise function
        result = recognise(image_data)
        assert isinstance(result, str)
        assert len(result) > 0, "OCR result should not be empty"
