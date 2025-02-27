"""Tests for model validation and compatibility between SQLAlchemy models and Pydantic schemas."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.sql import select

from app.models import Profile, Medication
from app.schemas import (
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
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.updated_at, datetime)

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
        test_db_session.add(profile)
        test_db_session.commit()
        test_db_session.refresh(profile)

        # Convert to response schema
        response = ProfileResponse.model_validate(profile)
        assert response.id == profile.id
        assert response.username == profile.username
        assert response.bio == profile.bio
        assert response.created_at == profile.created_at
        assert response.updated_at == profile.updated_at


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
        assert isinstance(medication.created_at, datetime)
        assert isinstance(medication.updated_at, datetime)

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

        # Convert to response schema
        response = MedicationResponse.model_validate(medication)
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
    test_db_session.refresh(profile)

    # Create 2 medications for the profile
    for i in range(2):
        medication = Medication(
            profile_id=profile.id,
            title=f"Test Medication {i}",
            active_ingredients="Test Ingredient",
            dosage="10mg",
            scanned_text="Test scan text",
            prescription_details={"frequency": "daily"},
            scan_url=f"https://example.com/test_image_{i}.jpg",
        )
        test_db_session.add(medication)
    test_db_session.commit()

    # Test relationship from profile to medications
    stmt = select(Profile).where(Profile.id == profile.id)
    result = test_db_session.execute(stmt).scalar_one()
    assert len(result.medications) == 2
    assert all(med.profile_id == profile.id for med in result.medications)

    # Test cascade delete
    test_db_session.delete(profile)
    test_db_session.commit()

    # Verify all related medications are deleted
    stmt = select(Medication).where(Medication.profile_id == profile.id)
    result = test_db_session.execute(stmt).scalars().all()
    assert len(result) == 0
