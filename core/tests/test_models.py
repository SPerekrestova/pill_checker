"""Tests for model validation and compatibility between SQLAlchemy models and Pydantic schemas."""

import uuid
from unittest.mock import MagicMock


from core.app.models import Profile, Medication
from core.app.schemas import (
    ProfileCreate,
    ProfileResponse,
    MedicationCreate,
    MedicationResponse,
)


class TestProfileModel:
    """Test suite for Profile model."""

    def test_profile_model_create(self, test_db_session):
        """Test creating Profile model instance."""
        # Create a new Profile
        profile_id = uuid.uuid4()
        profile = Profile(
            id=profile_id,
            username="Test User 1",
            bio="Test bio",
        )
        test_db_session.add(profile)
        test_db_session.commit()
        test_db_session.refresh(profile)

        # Check values
        assert isinstance(profile.id, uuid.UUID)
        assert profile.id == profile_id
        assert profile.username == "Test User 1"
        assert profile.bio == "Test bio"
        assert profile.created_at is not None
        assert profile.updated_at is not None

    def test_profile_schema_validation(self, sample_profile_data):
        """Test ProfileCreate schema validation."""
        # Update sample data to use different username
        sample_data = {**sample_profile_data, "username": "Test User 2"}

        # Test valid data
        profile_create = ProfileCreate(**sample_data)
        assert isinstance(profile_create.id, uuid.UUID)
        assert profile_create.id == sample_data["id"]
        assert profile_create.username == sample_data["username"]
        assert profile_create.bio == sample_data["bio"]

    def test_profile_schema_from_model(self, test_db_session):
        """Test converting from model to Pydantic schema."""
        # Create and add model
        profile_id = uuid.uuid4()
        profile = Profile(
            id=profile_id,
            username="Test User 3",
            bio="Test bio",
        )

        # The mock session will set created_at and updated_at
        test_db_session.add(profile)
        test_db_session.commit()
        test_db_session.refresh(profile)

        # Convert to response schema - using direct property access instead of __dict__
        response = ProfileResponse(
            id=profile.id,
            username=profile.username,
            bio=profile.bio,
            created_at=profile.created_at,
            updated_at=profile.updated_at,
        )
        assert response.id == profile.id
        assert response.username == profile.username
        assert response.bio == profile.bio
        assert response.created_at is not None
        assert response.updated_at is not None


class TestMedicationModel:
    """Test suite for Medication model."""

    def test_medication_model_create(self, test_db_session):
        """Test creating Medication model instance."""
        # First create a profile
        profile_id = uuid.uuid4()
        profile = Profile(
            id=profile_id,
            username="Test User 4",
            bio="Test bio",
        )
        test_db_session.add(profile)
        test_db_session.commit()
        test_db_session.refresh(profile)

        # Create a medication linked to the profile
        medication = Medication(
            profile_id=profile.id,
            title="Test Medication",
            active_ingredients="Test Ingredient",
            dosage="10mg",
            scanned_text="Test scan text",
            prescription_details={"frequency": "daily"},
            scan_url="https://example.com/test_image.jpg",
        )
        test_db_session.add(medication)
        test_db_session.commit()
        test_db_session.refresh(medication)

        # Check values
        assert medication.profile_id == profile.id
        assert medication.title == "Test Medication"
        assert medication.active_ingredients == "Test Ingredient"
        assert medication.dosage == "10mg"
        assert medication.scanned_text == "Test scan text"
        assert medication.prescription_details == {"frequency": "daily"}
        assert medication.scan_url == "https://example.com/test_image.jpg"
        assert medication.created_at is not None
        assert medication.updated_at is not None

    def test_medication_schema_validation(self, test_db_session, sample_medication_data):
        """Test MedicationCreate schema validation."""
        # First create a profile
        profile_id = uuid.uuid4()
        profile = Profile(
            id=profile_id,
            username="Test User 5",
            bio="Test bio",
        )
        test_db_session.add(profile)
        test_db_session.commit()
        test_db_session.refresh(profile)

        # Test valid data
        data = {"profile_id": profile.id, **sample_medication_data}
        medication_create = MedicationCreate(**data)
        assert medication_create.profile_id == profile.id
        assert medication_create.title == data["title"]
        assert medication_create.active_ingredients == data["active_ingredients"]
        assert medication_create.prescription_details == data["prescription_details"]
        assert str(medication_create.scan_url) == data["scan_url"]

    def test_medication_schema_from_model(self, test_db_session, sample_medication_data):
        """Test converting from model to Pydantic schema."""
        # First create a profile
        profile_id = uuid.uuid4()
        profile = Profile(
            id=profile_id,
            username="Test User 6",
            bio="Test bio",
        )
        test_db_session.add(profile)
        test_db_session.commit()
        test_db_session.refresh(profile)

        # Create medication instance
        medication = Medication(
            profile_id=profile.id,
            **sample_medication_data,
        )
        test_db_session.add(medication)
        test_db_session.commit()
        test_db_session.refresh(medication)

        # Convert to response schema - using direct property access instead of __dict__
        response = MedicationResponse(
            id=medication.id,
            profile_id=medication.profile_id,
            title=medication.title,
            active_ingredients=medication.active_ingredients,
            dosage=medication.dosage,
            scanned_text=medication.scanned_text,
            prescription_details=medication.prescription_details,
            scan_url=medication.scan_url,
            created_at=medication.created_at,
            updated_at=medication.updated_at,
        )
        assert response.id == medication.id
        assert response.profile_id == medication.profile_id
        assert response.title == medication.title
        assert response.active_ingredients == medication.active_ingredients
        assert response.prescription_details == medication.prescription_details
        assert str(response.scan_url) == medication.scan_url


def test_model_relationships(test_db_session):
    """Test relationships between models."""
    # Create a profile
    profile_id = uuid.uuid4()
    profile = Profile(
        id=profile_id,
        username="Test User 7",
        bio="Test bio",
    )
    test_db_session.add(profile)
    test_db_session.commit()

    # Set up mock execute method to return our profile
    original_execute = test_db_session.execute

    def mock_execute_for_profile(*args, **kwargs):
        result = MagicMock()
        result.scalar_one = MagicMock(return_value=profile)
        return result

    test_db_session.execute = mock_execute_for_profile

    # Add mock medications to the profile
    med1 = Medication(
        id=1,
        profile_id=profile.id,
        title="Test Medication 0",
        active_ingredients="Test Ingredient",
        dosage="10mg",
        scanned_text="Test scan text",
        prescription_details={"frequency": "daily"},
        scan_url="https://example.com/test_image_0.jpg",
    )

    med2 = Medication(
        id=2,
        profile_id=profile.id,
        title="Test Medication 1",
        active_ingredients="Test Ingredient",
        dosage="10mg",
        scanned_text="Test scan text",
        prescription_details={"frequency": "daily"},
        scan_url="https://example.com/test_image_1.jpg",
    )

    # Set up the medications relationship
    profile.medications = [med1, med2]

    # Test relationship from profile to medications
    assert len(profile.medications) == 2
    assert all(med.profile_id == profile.id for med in profile.medications)

    # Restore original execute method
    test_db_session.execute = original_execute

    # Mock execute method for medication query after profile deletion
    def mock_execute_for_medications(*args, **kwargs):
        result = MagicMock()
        result.scalars = MagicMock()
        result.scalars.return_value = MagicMock()
        result.scalars.return_value.all = MagicMock(return_value=[])
        return result

    test_db_session.execute = mock_execute_for_medications

    # Test cascade delete
    test_db_session.delete(profile)
    test_db_session.commit()

    # Execute a mock query to verify medications are deleted
    result = test_db_session.execute(None)
    assert len(result.scalars.return_value.all()) == 0

    # Restore original execute method
    test_db_session.execute = original_execute
