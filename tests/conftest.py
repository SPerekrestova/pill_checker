"""Test configuration and fixtures."""

from pill_checker.services.ocr import EasyOCRClient
from pill_checker.models import Medication, Profile
from pill_checker.main import app
from pill_checker.core.config import Settings
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Load test environment variables
test_env_path = Path(__file__).parent.parent / ".env.test"
if test_env_path.exists():
    load_dotenv(test_env_path, override=True)
else:
    # Set minimal required environment variables if .env.test doesn't exist
    os.environ.update(
        {
            "APP_ENV": "testing",
            "SECRET_KEY": "test-secret-key",
            "SUPABASE_URL": "http://localhost:8000",
            "SUPABASE_KEY": "test-key",
            "SUPABASE_SERVICE_ROLE_KEY": "test-service-role-key",
            "DATABASE_URL": "postgresql://postgres:postgres@localhost:5432/test_db",
            "SKIP_REAL_OCR_TESTS": "True",
        }
    )

# Now import the application modules

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
        """Initialize mock client without loading actual models."""
        self.languages = languages or ["en"]
        self.reader = MagicMock()

    def read_text(self, image_data):
        """Return mock text instead of performing actual OCR."""
        return "Mocked OCR text for testing"


@pytest.fixture(autouse=True)
def mock_ocr_service():
    """Mock the OCR service using our custom client."""
    global _original_ocr_client

    # Skip if SKIP_REAL_OCR_TESTS is set
    if os.environ.get("SKIP_REAL_OCR_TESTS", "").lower() == "true":
        # Save original OCR client
        _original_ocr_client = getattr(app.services.ocr_service, "_ocr_client", None)

        # Set mock client
        mock_client = MockOCRClient()
        app.services.ocr_service._ocr_client = mock_client

        yield mock_client

        # Reset to original client
        if _original_ocr_client:
            app.services.ocr_service._ocr_client = _original_ocr_client
    else:
        # Don't mock if we want to run real OCR tests
        yield None


@pytest.fixture(autouse=True)
def mock_supabase_client():
    """Mock Supabase client for all tests."""
    mock_client = MagicMock()

    # Mock both the auth service and medications API
    with (
        patch("pill_checker.services.auth.create_client") as mock_auth_create,
        patch("pill_checker.api.v1.medications.get_supabase_client") as mock_med_get,
    ):
        mock_auth_create.return_value = mock_client
        mock_med_get.return_value = mock_client

        yield mock_client


@pytest.fixture
def disable_rate_limiting():
    """Disable rate limiting for tests."""
    with patch("pill_checker.core.security.limiter.enabled", False):
        yield


@pytest.fixture
def sample_ner_entities():
    """Sample NER entities response for testing (actual API structure)."""
    return [
        {
            "text": "ibuprofen",
            "umls_entities": [
                {
                    "canonical_name": "Ibuprofen",
                    "definition": "A nonsteroidal anti-inflammatory drug",
                    "aliases": ["Advil", "Motrin", "Nurofen"],
                }
            ],
        },
        {
            "text": "pain",
            "umls_entities": [
                {
                    "canonical_name": "Pain",
                    "definition": "An unpleasant sensory experience",
                    "aliases": [],
                }
            ],
        },
    ]


@pytest.fixture
def mock_ner_client(sample_ner_entities):
    """Mock NER client for testing."""
    mock_client = MagicMock()
    mock_client.extract_entities.return_value = sample_ner_entities
    mock_client.find_active_ingredients.return_value = ["Ibuprofen", "Pain"]
    mock_client.get_entity_details.return_value = sample_ner_entities
    return mock_client


@pytest.fixture(autouse=True)
def mock_ner_service(mock_ner_client):
    """Mock the NER service globally for tests."""
    with patch(
        "pill_checker.services.biomed_ner_client.get_ner_client", return_value=mock_ner_client
    ):
        yield mock_ner_client
