"""Generate a test image with text for OCR testing.

This script creates test images with medication-like text, suitable for OCR testing.
It can be used standalone or imported by the test suite to generate test data.
"""

import os
import sys
import tempfile
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont


def create_test_image(
    text="Sample Prescription",
    filename="test_prescription.png",
    output_dir=None,
    include_details=True,
):
    """Create a test image with text.

    Args:
        text: Main text to include on the image
        filename: Name of the output file
        output_dir: Directory to save image (defaults to tests/test_images)
        include_details: Whether to include additional medication details

    Returns:
        Path to the created image
    """
    # Create a blank image with white background
    width, height = 800, 400
    img = Image.new("RGB", (width, height), color="white")
    draw = ImageDraw.Draw(img)

    # Try to use a system font
    try:
        # Try to find a font that's likely to be on most systems
        font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows
            "/Library/Fonts/Arial.ttf",  # Another macOS location
        ]

        font = None
        for path in font_paths:
            if os.path.exists(path):
                font = ImageFont.truetype(path, 40)
                break

        if font is None:
            # Fallback to default
            font = ImageFont.load_default()

    except Exception:
        # If there's any error, use the default font
        font = ImageFont.load_default()

    # Add text to the image
    main_text = text
    draw.text((50, 50), main_text, fill="black", font=font)

    # Add additional medication-like text if requested
    if include_details:
        medication_text = [
            "TAKE ONE TABLET DAILY",
            "Active ingredient: Ibuprofen 200mg",
            "KEEP OUT OF REACH OF CHILDREN",
            "Store at room temperature",
            "Mfg date: 01/2023   Exp date: 01/2025",
        ]

        y_position = 120
        for line in medication_text:
            draw.text((50, y_position), line, fill="black", font=font)
            y_position += 50

    # Determine output directory
    if output_dir is None:
        # Default to tests/test_images relative to this script
        output_dir = Path(__file__).parent.parent / "test_images"
    else:
        output_dir = Path(output_dir)

    # Create the directory if it doesn't exist
    output_dir.mkdir(exist_ok=True, parents=True)

    # Save the image
    output_path = output_dir / filename
    img.save(output_path)
    print(f"Test image created at: {output_path}")

    return output_path


def create_multiple_test_images(output_dir=None, count=3):
    """Create multiple test images with different text and formats.

    Args:
        output_dir: Directory to save images (defaults to tests/test_images)
        count: Number of images to create (max 3)

    Returns:
        List of paths to created images
    """
    # Limit the count to avoid creating too many images
    count = min(count, 3)

    # Define image configurations
    configurations = [
        {
            "text": "Sample Prescription",
            "filename": "test_prescription.png",
            "include_details": True,
        },
        {
            "text": "MEDICATION INFORMATION\nParacetamol 500mg",
            "filename": "test_medication_info.png",
            "include_details": False,
        },
        {
            "text": "DOSAGE INSTRUCTIONS",
            "filename": "test_dosage.png",
            "include_details": True,
        },
    ]

    created_images = []
    for i in range(count):
        config = configurations[i]
        path = create_test_image(
            text=config["text"],
            filename=config["filename"],
            output_dir=output_dir,
            include_details=config["include_details"],
        )
        created_images.append(path)

    return created_images


# Actual tests that will be included in the test suite


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test image output."""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_create_single_image(temp_dir):
    """Test that a single test image can be created."""
    image_path = create_test_image(
        text="Test Image", filename="test_image.png", output_dir=temp_dir
    )

    # Verify the file exists
    assert image_path.exists()

    # Verify it's a valid image file
    img = Image.open(image_path)
    assert img.size == (800, 400)
    assert img.mode == "RGB"


def test_create_image_without_details(temp_dir):
    """Test that an image can be created without medication details."""
    image_path = create_test_image(
        text="No Details",
        filename="no_details.png",
        output_dir=temp_dir,
        include_details=False,
    )

    # Verify the file exists
    assert image_path.exists()

    # Verify it's a valid image file
    img = Image.open(image_path)
    assert img.size == (800, 400)


def test_create_multiple_images(temp_dir):
    """Test creating multiple test images."""
    image_paths = create_multiple_test_images(output_dir=temp_dir, count=2)

    # Verify we got exactly 2 images
    assert len(image_paths) == 2

    # Verify all files exist
    for path in image_paths:
        assert path.exists()

        # Verify they're valid images
        img = Image.open(path)
        assert img.size == (800, 400)


if __name__ == "__main__":
    # When run as a script, create multiple test images
    output_dir = None
    count = 1

    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1].isdigit():
            count = int(sys.argv[1])
        else:
            output_dir = sys.argv[1]

    if len(sys.argv) > 2 and sys.argv[2].isdigit():
        count = int(sys.argv[2])

    create_multiple_test_images(output_dir, count)
