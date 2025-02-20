from datetime import datetime
from typing import Optional
from pydantic import HttpUrl

from .base import BaseSchema


class UploadedImageBase(BaseSchema):
    """Base schema for uploaded image."""
    image: str
    file_path: Optional[str] = None


class UploadedImageCreate(UploadedImageBase):
    """Schema for creating an uploaded image."""
    pass


class UploadedImageUpdate(UploadedImageBase):
    """Schema for updating an uploaded image."""
    image: Optional[str] = None


class UploadedImageInDB(UploadedImageBase):
    """Schema for uploaded image in database."""
    id: int
    uploaded_at: datetime


class UploadedImageResponse(UploadedImageInDB):
    """Schema for uploaded image response."""
    image_url: Optional[HttpUrl] = None 