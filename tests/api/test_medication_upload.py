"""Integration tests for medication upload with NER functionality."""

import io
import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from pill_checker.main import app
from pill_checker.models.medication import Medication


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_current_user():
    """Mock authenticated user."""
    return {
        "id": str(uuid.uuid4()),
        "email": "test@example.com",
        "profile": {"username": "testuser"},
    }


@pytest.fixture
def sample_medication_image():
    """Create a sample medication image for testing."""
    # Create a simple test image
    img = Image.new("RGB", (100, 100), color="white")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes


class TestMedicationUploadIntegration:
    """Integration tests for medication upload endpoint."""

    @patch("pill_checker.api.v1.medications.get_current_user")
    @patch("pill_checker.api.v1.medications.get_db")
    @patch("pill_checker.api.v1.medications.get_supabase_client")
    @patch("pill_checker.services.ocr.get_ocr_client")
    def test_upload_medication_success(
        self,
        mock_get_ocr,
        mock_get_supabase,
        mock_get_db,
        mock_get_user,
        test_client,
        mock_current_user,
        sample_medication_image,
        mock_ner_client,
    ):
        """Test successful medication upload with NER integration."""
        # Setup mocks
        mock_get_user.return_value = mock_current_user

        # Mock database
        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        def mock_refresh(medication):
            medication.id = 1
            medication.created_at = "2025-01-01T00:00:00"
            medication.updated_at = "2025-01-01T00:00:00"

        mock_db.refresh = mock_refresh
        mock_get_db.return_value = mock_db

        # Mock Supabase storage
        mock_supabase = MagicMock()
        mock_storage = MagicMock()
        mock_supabase.storage.from_.return_value = mock_storage
        mock_get_supabase.return_value = mock_supabase

        # Mock OCR client
        mock_ocr_client = MagicMock()
        mock_ocr_client.read_text.return_value = "Ibuprofen 200mg tablets. Take for pain."
        mock_get_ocr.return_value = mock_ocr_client

        # Make request
        files = {"image": ("medication.png", sample_medication_image, "image/png")}
        response = test_client.post("/api/v1/medications/upload", files=files)

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify structured data was extracted
        assert data["title"] is not None
        assert "Ibuprofen" in data["title"]
        assert data["active_ingredients"] == "Ibuprofen"
        assert data["dosage"] == "200mg"
        assert data["scanned_text"] == "Ibuprofen 200mg tablets. Take for pain."
        assert data["prescription_details"] is not None

        # Verify OCR was called
        mock_ocr_client.read_text.assert_called_once()

        # Verify NER was called
        mock_ner_client.extract_entities.assert_called_once_with(
            "Ibuprofen 200mg tablets. Take for pain."
        )

        # Verify storage upload was called
        mock_storage.upload.assert_called_once()

        # Verify database operations
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()

    @patch("pill_checker.api.v1.medications.get_current_user")
    @patch("pill_checker.api.v1.medications.get_db")
    @patch("pill_checker.api.v1.medications.get_supabase_client")
    @patch("pill_checker.services.ocr.get_ocr_client")
    def test_upload_medication_ner_failure_graceful(
        self,
        mock_get_ocr,
        mock_get_supabase,
        mock_get_db,
        mock_get_user,
        test_client,
        mock_current_user,
        sample_medication_image,
        mock_ner_client,
    ):
        """Test that medication upload succeeds even if NER fails."""
        # Setup mocks
        mock_get_user.return_value = mock_current_user

        mock_db = MagicMock()
        mock_db.add = MagicMock()
        mock_db.commit = MagicMock()

        def mock_refresh(medication):
            medication.id = 1
            medication.created_at = "2025-01-01T00:00:00"
            medication.updated_at = "2025-01-01T00:00:00"

        mock_db.refresh = mock_refresh
        mock_get_db.return_value = mock_db

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase

        mock_ocr_client = MagicMock()
        mock_ocr_client.read_text.return_value = "Some medication text"
        mock_get_ocr.return_value = mock_ocr_client

        # Make NER fail
        mock_ner_client.extract_entities.side_effect = RuntimeError("NER service down")

        # Make request
        files = {"image": ("medication.png", sample_medication_image, "image/png")}
        response = test_client.post("/api/v1/medications/upload", files=files)

        # Should still succeed with OCR text only
        assert response.status_code == 200
        data = response.json()
        assert data["scanned_text"] == "Some medication text"

    @patch("pill_checker.api.v1.medications.get_current_user")
    @patch("pill_checker.api.v1.medications.get_db")
    @patch("pill_checker.api.v1.medications.get_supabase_client")
    @patch("pill_checker.services.ocr.get_ocr_client")
    def test_upload_medication_multiple_ingredients(
        self,
        mock_get_ocr,
        mock_get_supabase,
        mock_get_db,
        mock_get_user,
        test_client,
        mock_current_user,
        sample_medication_image,
        mock_ner_client,
    ):
        """Test upload with multiple active ingredients."""
        # Setup mocks
        mock_get_user.return_value = mock_current_user

        mock_db = MagicMock()

        def mock_refresh(medication):
            medication.id = 1
            medication.created_at = "2025-01-01T00:00:00"
            medication.updated_at = "2025-01-01T00:00:00"

        mock_db.refresh = mock_refresh
        mock_get_db.return_value = mock_db

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase

        mock_ocr_client = MagicMock()
        mock_ocr_client.read_text.return_value = (
            "Amoxicillin 500mg and Clavulanic Acid 125mg tablets"
        )
        mock_get_ocr.return_value = mock_ocr_client

        # Mock NER to return multiple chemicals
        mock_ner_client.extract_entities.return_value = [
            {
                "text": "Amoxicillin",
                "label": "CHEMICAL",
                "canonical_name": "Amoxicillin",
                "cui": "C0002645",
            },
            {
                "text": "Clavulanic Acid",
                "label": "CHEMICAL",
                "canonical_name": "Clavulanic Acid",
                "cui": "C0054066",
            },
        ]

        # Make request
        files = {"image": ("medication.png", sample_medication_image, "image/png")}
        response = test_client.post("/api/v1/medications/upload", files=files)

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify both ingredients are captured
        assert "Amoxicillin" in data["active_ingredients"]
        assert "Clavulanic Acid" in data["active_ingredients"]
        assert "Amoxicillin" in data["title"]
        assert data["dosage"] == "500mg"

        # Verify CUIs are stored
        assert "cui_identifiers" in data["prescription_details"]
        assert "C0002645" in data["prescription_details"]["cui_identifiers"]
        assert "C0054066" in data["prescription_details"]["cui_identifiers"]

    @patch("pill_checker.api.v1.medications.get_current_user")
    @patch("pill_checker.api.v1.medications.get_db")
    @patch("pill_checker.api.v1.medications.get_supabase_client")
    @patch("pill_checker.services.ocr.get_ocr_client")
    def test_upload_medication_with_disease_entities(
        self,
        mock_get_ocr,
        mock_get_supabase,
        mock_get_db,
        mock_get_user,
        test_client,
        mock_current_user,
        sample_medication_image,
        mock_ner_client,
    ):
        """Test upload extracts disease entities."""
        # Setup mocks
        mock_get_user.return_value = mock_current_user

        mock_db = MagicMock()

        def mock_refresh(medication):
            medication.id = 1
            medication.created_at = "2025-01-01T00:00:00"
            medication.updated_at = "2025-01-01T00:00:00"

        mock_db.refresh = mock_refresh
        mock_get_db.return_value = mock_db

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase

        mock_ocr_client = MagicMock()
        mock_ocr_client.read_text.return_value = "Aspirin 100mg for headache and fever"
        mock_get_ocr.return_value = mock_ocr_client

        # Mock NER to return chemical and diseases
        mock_ner_client.extract_entities.return_value = [
            {
                "text": "Aspirin",
                "label": "CHEMICAL",
                "canonical_name": "Aspirin",
            },
            {
                "text": "headache",
                "label": "DISEASE",
                "canonical_name": "Headache",
            },
            {
                "text": "fever",
                "label": "DISEASE",
                "canonical_name": "Fever",
            },
        ]

        # Make request
        files = {"image": ("medication.png", sample_medication_image, "image/png")}
        response = test_client.post("/api/v1/medications/upload", files=files)

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify disease entities are stored in prescription details
        assert "related_conditions" in data["prescription_details"]
        assert "Headache" in data["prescription_details"]["related_conditions"]
        assert "Fever" in data["prescription_details"]["related_conditions"]

    @patch("pill_checker.api.v1.medications.get_current_user")
    def test_upload_medication_unauthorized(self, mock_get_user, test_client, sample_medication_image):
        """Test that upload requires authentication."""
        mock_get_user.side_effect = Exception("Unauthorized")

        files = {"image": ("medication.png", sample_medication_image, "image/png")}
        response = test_client.post("/api/v1/medications/upload", files=files)

        # Should fail with 500 (or could be 401 depending on exception handling)
        assert response.status_code in [401, 500]

    @patch("pill_checker.api.v1.medications.get_current_user")
    @patch("pill_checker.api.v1.medications.get_db")
    @patch("pill_checker.api.v1.medications.get_supabase_client")
    @patch("pill_checker.services.ocr.get_ocr_client")
    def test_upload_medication_extracts_prescription_details(
        self,
        mock_get_ocr,
        mock_get_supabase,
        mock_get_db,
        mock_get_user,
        test_client,
        mock_current_user,
        sample_medication_image,
        mock_ner_client,
    ):
        """Test that prescription details are properly extracted."""
        # Setup mocks
        mock_get_user.return_value = mock_current_user

        mock_db = MagicMock()

        def mock_refresh(medication):
            medication.id = 1
            medication.created_at = "2025-01-01T00:00:00"
            medication.updated_at = "2025-01-01T00:00:00"

        mock_db.refresh = mock_refresh
        mock_get_db.return_value = mock_db

        mock_supabase = MagicMock()
        mock_get_supabase.return_value = mock_supabase

        mock_ocr_client = MagicMock()
        mock_ocr_client.read_text.return_value = (
            "Ibuprofen 200mg. Take twice daily in the morning. Exp: 12/2025"
        )
        mock_get_ocr.return_value = mock_ocr_client

        # Make request
        files = {"image": ("medication.png", sample_medication_image, "image/png")}
        response = test_client.post("/api/v1/medications/upload", files=files)

        # Assert response
        assert response.status_code == 200
        data = response.json()

        # Verify prescription details
        details = data["prescription_details"]
        assert "frequency" in details
        assert "timing" in details
        assert "morning" in details["timing"].lower()
        assert "expiry_date" in details
        assert "12/2025" in details["expiry_date"]
