from typing import Optional, List, UUID
from pydantic import Field

from .base import TimestampedSchema
from .medication import MedicationResponse


class ProfileBase(TimestampedSchema):
    """Base schema for user profile."""
    display_name: Optional[str] = None
    bio: Optional[str] = None


class ProfileCreate(ProfileBase):
    """Schema for creating a profile."""
    user_id: UUID


class ProfileUpdate(ProfileBase):
    """Schema for updating a profile."""
    display_name: Optional[str] = None
    bio: Optional[str] = None


class ProfileInDB(ProfileBase):
    """Schema for profile in database."""
    id: int
    user_id: UUID


class ProfileResponse(ProfileInDB):
    """Schema for profile response."""
    medications: Optional[List[MedicationResponse]] = Field(default_factory=list)


class ProfileWithStats(ProfileResponse):
    """Schema for profile with additional statistics."""
    total_medications: int = 0
    active_medications: int = 0
    last_scan_date: Optional[str] = None 