"""Tests for model validation and compatibility between SQLAlchemy models and Pydantic schemas."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from app.models import Profile, Medication, ScannedImage
from app.schemas import (
    ProfileCreate,
    ProfileResponse,
    MedicationCreate,
    MedicationResponse,
    ScannedImageCreate,
    ScannedImageResponse,
)


class TestProfileModel:
    """Test suite for Profile model and schemas."""

    def test_profile_model_create(self, test_db_session, sample_profile_data):
        """Test creating a Profile model instance."""
        profile = Profile(**sample_profile_data)
        test_db_session.add(profile)
        test_db_session.commit()

        assert profile.id is not None
        assert isinstance(profile.user_id, uuid.UUID)
        assert profile.user_id == sample_profile_data["user_id"]
        assert profile.display_name == sample_profile_data["display_name"]
        assert profile.bio == sample_profile_data["bio"]
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.updated_at, datetime)

    def test_profile_schema_validation(self, sample_profile_data):
        """Test Pydantic schema validation for Profile."""
        # Test successful validation
        profile_create = ProfileCreate(**sample_profile_data)
        assert isinstance(profile_create.user_id, uuid.UUID)
        assert profile_create.user_id == sample_profile_data["user_id"]

        # Test validation error for invalid UUID
        with pytest.raises(ValidationError):
            ProfileCreate(
                user_id="invalid-uuid",
                **{k: v for k, v in sample_profile_data.items() if k != "user_id"}
            )

    def test_profile_schema_from_model(self, test_db_session, sample_profile_data):
        """Test converting Profile model to Pydantic schema."""
        profile = Profile(**sample_profile_data)
        test_db_session.add(profile)
        test_db_session.commit()

        profile_response = ProfileResponse.from_orm(profile)
        assert profile_response.id == profile.id
        assert isinstance(profile_response.user_id, uuid.UUID)
        assert profile_response.user_id == profile.user_id
        assert profile_response.display_name == profile.display_name
        assert profile_response.bio == profile.bio


class TestMedicationModel:
    """Test suite for Medication model and schemas."""

    def test_medication_model_create(
        self, test_db_session, sample_profile_data, sample_medication_data
    ):
        """Test creating a Medication model instance."""
        # Create a profile first
        profile = Profile(**sample_profile_data)
        test_db_session.add(profile)
        test_db_session.commit()

        # Remove image_url from model data as it's only required for schema
        model_data = {k: v for k, v in sample_medication_data.items() if k != "image_url"}
        medication = Medication(profile_id=profile.id, **model_data)
        test_db_session.add(medication)
        test_db_session.commit()

        assert medication.id is not None
        assert medication.profile_id == profile.id
        assert medication.title == model_data["title"]
        assert medication.active_ingredients == model_data["active_ingredients"]
        assert medication.prescription_details == model_data["prescription_details"]
        assert isinstance(medication.scan_date, datetime)
        assert medication.image_url is None  # image_url should be None by default

    def test_medication_schema_validation(
        self, test_db_session, sample_profile_data, sample_medication_data
    ):
        """Test Pydantic schema validation for Medication."""
        # Create a profile first
        profile = Profile(**sample_profile_data)
        test_db_session.add(profile)
        test_db_session.commit()

        # Test successful validation
        medication_create = MedicationCreate(profile_id=profile.id, **sample_medication_data)
        assert medication_create.profile_id == profile.id
        assert medication_create.title == sample_medication_data["title"]

        # Test validation error for non-existent profile_id
        with pytest.raises(ValidationError):
            MedicationCreate(profile_id=-1, **sample_medication_data)

    def test_medication_schema_from_model(
        self, test_db_session, sample_profile_data, sample_medication_data
    ):
        """Test converting Medication model to Pydantic schema."""
        # Create a profile first
        profile = Profile(**sample_profile_data)
        test_db_session.add(profile)
        test_db_session.commit()

        # Remove image_url from model data as it's only required for schema
        model_data = {k: v for k, v in sample_medication_data.items() if k != "image_url"}
        medication = Medication(profile_id=profile.id, **model_data)
        test_db_session.add(medication)
        test_db_session.commit()

        medication_response = MedicationResponse.from_orm(medication)
        assert medication_response.id == medication.id
        assert medication_response.profile_id == medication.profile_id
        assert medication_response.title == medication.title
        assert medication_response.prescription_details == medication.prescription_details
        assert medication_response.image_url is None  # image_url should be None in response


class TestScannedImageModel:
    """Test suite for ScannedImage model and schemas."""

    def test_scanned_image_model_create(self, test_db_session, sample_scanned_image_data):
        """Test creating a ScannedImage model instance."""
        image = ScannedImage(**sample_scanned_image_data)
        test_db_session.add(image)
        test_db_session.commit()

        assert image.id is not None
        assert image.image == sample_scanned_image_data["image"]
        assert image.file_path == sample_scanned_image_data["file_path"]
        assert isinstance(image.uploaded_at, datetime)

    def test_scanned_image_schema_validation(self, sample_scanned_image_data):
        """Test Pydantic schema validation for ScannedImage."""
        # Test successful validation
        image_create = ScannedImageCreate(**sample_scanned_image_data)
        assert image_create.image == sample_scanned_image_data["image"]

        # Test validation error for missing required field
        with pytest.raises(ValidationError):
            ScannedImageCreate(file_path=sample_scanned_image_data["file_path"])

    def test_scanned_image_schema_from_model(self, test_db_session, sample_scanned_image_data):
        """Test converting ScannedImage model to Pydantic schema."""
        image = ScannedImage(**sample_scanned_image_data)
        test_db_session.add(image)
        test_db_session.commit()

        image_response = ScannedImageResponse.from_orm(image)
        assert image_response.id == image.id
        assert image_response.image == image.image
        assert image_response.file_path == image.file_path


def test_model_relationships(test_db_session, sample_profile_data, sample_medication_data):
    """Test relationships between models."""
    # Create profile
    profile = Profile(**sample_profile_data)
    test_db_session.add(profile)
    test_db_session.commit()

    # Create medication linked to profile
    # Remove image_url from model data as it's only required for schema
    model_data = {k: v for k, v in sample_medication_data.items() if k != "image_url"}
    medication = Medication(profile_id=profile.id, **model_data)
    test_db_session.add(medication)
    test_db_session.commit()

    # Test relationship from profile to medications
    assert len(profile.medications) == 1
    assert profile.medications[0].id == medication.id

    # Test relationship from medication to profile
    assert medication.profile.id == profile.id

    # Test cascade delete
    test_db_session.delete(profile)
    test_db_session.commit()

    # Verify medication was also deleted
    assert test_db_session.query(Medication).filter_by(id=medication.id).first() is None
