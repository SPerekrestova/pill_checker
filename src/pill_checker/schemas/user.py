"""User schemas for FastAPI-Users authentication."""

import uuid
from typing import Optional

from fastapi_users import schemas
from pydantic import EmailStr


class UserRead(schemas.BaseUser[uuid.UUID]):
    """Schema for reading user data."""

    pass


class UserCreate(schemas.BaseUserCreate):
    """Schema for creating a new user."""

    email: EmailStr
    password: str
    username: Optional[str] = None


class UserUpdate(schemas.BaseUserUpdate):
    """Schema for updating user data."""

    password: Optional[str] = None
    email: Optional[EmailStr] = None
