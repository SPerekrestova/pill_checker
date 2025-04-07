"""Test configuration and fixtures."""

import os
import uuid
from datetime import datetime
from unittest.mock import MagicMock

import pytest
from sqlalchemy.orm import Session

from core.app.core.config import Settings
from core.app.main import app
from core.app.models import Medication, Profile
from core.app.services.ocr_service import EasyOCRClient

# Required for settings validation
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SUPABASE_URL"] = "http://localhost:8000"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret"

# Global variable to store the original OCR client
_original_ocr_client = None


def get_test_settings() -> Settings:
    """Get settings configured for testing."""
    return Settings()


@pytest.fixture(scope="session")
def test_settings():
    """Fixture for test settings."""
    return get_test_settings()


@pytest.fixture
def test_db_engine():
    """Create a mock database engine."""
    # We're not using a real engine, just mock it
    mock_engine = MagicMock()
    return mock_engine


@pytest.fixture
def test_db_session():
    """Create a mock database session."""
    mock_session = MagicMock(spec=Session)

    # Mock the add method
    mock_session.add = MagicMock()

    # Mock the commit method
    mock_session.commit = MagicMock()

    # Mock the refresh method to update the model with mock data
    def mock_refresh(model):
        if isinstance(model, Profile):
            # Set created_at and updated_at for Profile
            if not hasattr(model, "created_at") or model.created_at is None:
                model.created_at = datetime.now()
            if not hasattr(model, "updated_at") or model.updated_at is None:
                model.updated_at = datetime.now()

            # Add a mock medications relationship if it doesn't exist
            if not hasattr(model, "medications"):
                model.medications = []

        elif isinstance(model, Medication):
            # Set created_at and updated_at for Medication
            if not hasattr(model, "created_at") or model.created_at is None:
                model.created_at = datetime.now()
            if not hasattr(model, "updated_at") or model.updated_at is None:
                model.updated_at = datetime.now()

            # Set an ID if it doesn't exist
            if not hasattr(model, "id") or model.id is None:
                model.id = 1

    mock_session.refresh = mock_refresh

    # Mock execute for select statements
    def mock_execute(statement):
        result = MagicMock()

        # For Profile select statements
        result.scalar_one = MagicMock(return_value=None)

        # For Medication select statements
        result.scalars = MagicMock()
        result.scalars().all = MagicMock(return_value=[])

        return result

    mock_session.execute = mock_execute

    # Mock delete
    mock_session.delete = MagicMock()

    return mock_session


@pytest.fixture
def sample_profile_data():
    """Sample profile data for testing."""
    return {"id": uuid.uuid4(), "username": "Test User", "bio": "Test bio"}


@pytest.fixture
def sample_medication_data():
    """Sample medication data for testing."""
    return {
        "title": "Test Medication",
        "active_ingredients": "Test Ingredient",
        "scanned_text": "Test scan text",
        "dosage": "10mg",
        "prescription_details": {"frequency": "daily"},
        "scan_url": "https://example.com/test_image.jpg",
    }


class MockOCRClient(EasyOCRClient):
    """Mock OCR client for testing."""

    def __init__(self, languages=None):
        """Initialize without actual EasyOCR."""
        self.languages = languages or ["en"]
        # Skip real EasyOCR initialization

    def read_text(self, image_data):
        """Return mock text instead of performing actual OCR."""
        return "Mocked OCR text for testing"


@pytest.fixture(autouse=True)
def mock_ocr_service():
    """Mock the OCR service using our custom client."""
    global _original_ocr_client
    # Save original OCR client
    _original_ocr_client = app.services.ocr_service._ocr_client

    # Set mock client
    mock_client = MockOCRClient()
    app.services.ocr_service._ocr_client = mock_client

    yield mock_client

    # Reset to original client
    app.services.ocr_service._ocr_client = _original_ocr_client
