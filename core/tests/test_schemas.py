"""Tests for Pydantic schema validation and conversion."""

import uuid
from datetime import datetime

import pytest
from pydantic import ValidationError

from core.app.schemas import (
    ProfileCreate,
    ProfileUpdate,
    ProfileResponse,
    ProfileWithStats,
    MedicationCreate,
    MedicationUpdate,
)


class TestProfileSchemas:
    """Test suite for Profile-related schemas."""

    def test_profile_create_schema(self, sample_profile_data):
        """Test ProfileCreate schema validation."""
        # Test valid data
        profile = ProfileCreate(**sample_profile_data)
        assert isinstance(profile.id, uuid.UUID)
        assert profile.id == sample_profile_data["id"]
        assert profile.username == sample_profile_data["username"]
        assert profile.bio == sample_profile_data["bio"]

        # Test optional fields
        test_uuid = uuid.uuid4()
        profile = ProfileCreate(id=test_uuid)
        assert profile.id == test_uuid
        assert profile.username is None
        assert profile.bio is None

        # Test invalid UUID
        with pytest.raises(ValidationError):
            ProfileCreate(id="invalid-uuid")

    def test_profile_update_schema(self, sample_profile_data):
        """Test ProfileUpdate schema validation."""
        # Test partial update
        update_data = {"username": "Updated Name"}
        profile = ProfileUpdate(**update_data)
        assert profile.username == "Updated Name"
        assert profile.bio is None

        # Test full update
        profile = ProfileUpdate(**{k: v for k, v in sample_profile_data.items() if k != "id"})
        assert profile.username == sample_profile_data["username"]
        assert profile.bio == sample_profile_data["bio"]

    def test_profile_response_schema(self, sample_profile_data):
        """Test ProfileResponse schema."""
        data = {
            "id": sample_profile_data["id"],
            "username": sample_profile_data["username"],
            "bio": sample_profile_data["bio"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        response = ProfileResponse(**data)
        assert response.id == data["id"]
        assert isinstance(response.id, uuid.UUID)
        assert response.username == data["username"]
        assert response.bio == data["bio"]
        assert isinstance(response.created_at, datetime)
        assert isinstance(response.updated_at, datetime)


class TestMedicationSchemas:
    """Test suite for Medication-related schemas."""

    def test_medication_create_schema(self, sample_medication_data):
        """Test MedicationCreate schema validation."""
        # Test valid data
        data = {"profile_id": uuid.uuid4(), **sample_medication_data}
        medication = MedicationCreate(**data)
        assert medication.profile_id == data["profile_id"]
        assert medication.title == data["title"]
        assert medication.active_ingredients == data["active_ingredients"]
        assert medication.prescription_details == data["prescription_details"]
        assert str(medication.scan_url) == data["scan_url"]

        # Test validation error for missing required field
        with pytest.raises(ValidationError):
            MedicationCreate(profile_id=uuid.uuid4(), title="Test")

    def test_medication_update_schema(self, sample_medication_data):
        """Test MedicationUpdate schema validation."""
        # Test partial update
        update_data = {"title": "Updated Title"}
        medication = MedicationUpdate(**update_data)
        assert medication.title == "Updated Title"
        assert medication.active_ingredients is None

        # Test full update
        medication = MedicationUpdate(**sample_medication_data)
        assert medication.title == sample_medication_data["title"]
        assert medication.active_ingredients == sample_medication_data["active_ingredients"]


def test_schema_inheritance():
    """Test schema inheritance and base functionality."""
    # Test ProfileWithStats
    stats_data = {
        "id": uuid.uuid4(),
        "username": "Test User",
        "bio": "Test bio",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "total_medications": 5,
        "active_medications": 3,
        "last_scan_date": "2024-02-23",
    }
    profile_stats = ProfileWithStats(**stats_data)
    assert profile_stats.total_medications == 5
    assert profile_stats.active_medications == 3
    assert profile_stats.last_scan_date == "2024-02-23"
