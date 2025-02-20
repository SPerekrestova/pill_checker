from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import Field, HttpUrl

from .base import BaseSchema


class MedicationBase(BaseSchema):
    """Base schema for medication."""
    title: Optional[str] = None
    active_ingredients: Optional[str] = None
    scanned_text: Optional[str] = None
    dosage: Optional[str] = None
    prescription_details: Optional[Dict[str, Any]] = Field(default_factory=dict)


class MedicationCreate(MedicationBase):
    """Schema for creating a medication."""
    profile_id: int


class MedicationUpdate(MedicationBase):
    """Schema for updating a medication."""
    title: Optional[str] = None
    active_ingredients: Optional[str] = None
    dosage: Optional[str] = None
    prescription_details: Optional[Dict[str, Any]] = None


class MedicationInDB(MedicationBase):
    """Schema for medication in database."""
    id: int
    profile_id: int
    scan_date: datetime


class MedicationResponse(MedicationInDB):
    """Schema for medication response."""
    image_url: Optional[HttpUrl] = None
    status: str = "pending"
    status_color: str = "warning"  # Bootstrap color classes: primary, secondary, success, danger, warning, info

    @property
    def formatted_scan_date(self) -> str:
        """Return formatted scan date."""
        return self.scan_date.strftime("%Y-%m-%d %H:%M") 