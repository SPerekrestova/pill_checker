from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import Field, constr

from .base import BaseSchema


class MedicationBase(BaseSchema):
    """Base schema for medication."""

    title: Optional[constr(min_length=1, max_length=200)] = Field(
        None, description="Medication title"
    )
    active_ingredients: Optional[constr(min_length=1, max_length=500)] = Field(
        None, description="Active ingredients list"
    )
    scanned_text: Optional[constr(min_length=1)] = Field(
        None, description="Text extracted from image"
    )
    dosage: Optional[constr(min_length=1, max_length=100)] = Field(
        None, description="Medication dosage"
    )
    prescription_details: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional prescription details"
    )


class MedicationCreate(MedicationBase):
    """Schema for creating a medication."""

    profile_id: UUID = Field(..., description="Profile ID")
    scan_url: str = Field(..., description="URL of the uploaded medication scan")


class MedicationUpdate(MedicationBase):
    """Schema for updating a medication."""

    title: Optional[constr(min_length=1, max_length=200)] = None
    active_ingredients: Optional[constr(min_length=1, max_length=500)] = None
    dosage: Optional[constr(min_length=1, max_length=100)] = None
    prescription_details: Optional[Dict[str, Any]] = None


class MedicationInDB(MedicationBase):
    """Schema for medication in database."""

    id: int
    profile_id: UUID
    created_at: datetime
    updated_at: datetime


class MedicationResponse(MedicationInDB):
    """Schema for medication response."""

    scan_url: Optional[str] = Field(None, description="URL of the uploaded medication scan")


class PaginatedResponse(BaseSchema):
    """Schema for paginated response."""

    items: List[MedicationResponse]
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Items per page")
    pages: int = Field(..., description="Total number of pages")
