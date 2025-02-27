"""Test configuration and fixtures."""

import os
import uuid
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from datetime import datetime
from unittest.mock import patch, MagicMock

from app.core.config import Settings
from app.models import Base
from app.services.ocr_service import OCRClient, set_ocr_client

# Required for settings validation
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SUPABASE_URL"] = "http://localhost:8000"
os.environ["SUPABASE_KEY"] = "test-key"
os.environ["SUPABASE_JWT_SECRET"] = "test-jwt-secret"


def get_test_settings() -> Settings:
    """Get settings configured for testing."""
    return Settings()


@pytest.fixture(scope="session")
def test_settings():
    """Fixture for test settings."""
    return get_test_settings()


@pytest.fixture(scope="session")
def test_db_engine(test_settings):
    """Create a test database engine."""
    engine = create_engine(
        test_settings.SQLALCHEMY_DATABASE_URI,
        poolclass=StaticPool,
        echo=True,  # Enable SQL logging for debugging
    )

    # Drop all tables to ensure clean state
    with engine.connect() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.commit()

    # Create all tables
    Base.metadata.create_all(engine)

    yield engine

    # Clean up after tests
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_db_session(test_db_engine):
    """Create a test database session."""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


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


class MockOCRClient(OCRClient):
    """Mock OCR client for testing."""
    
    def read_text(self, image_data):
        """Return mock text instead of performing actual OCR."""
        return "Mocked OCR text for testing"


@pytest.fixture(autouse=True)
def mock_ocr_service():
    """Mock the OCR service using our custom client."""
    # Save original client to restore after test
    original_client = MagicMock()
    
    # Set mock client
    mock_client = MockOCRClient()
    set_ocr_client(mock_client)
    
    yield mock_client
    
    # Reset to default behavior
    set_ocr_client(None)
