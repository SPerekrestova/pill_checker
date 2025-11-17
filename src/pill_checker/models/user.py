"""User model for FastAPI-Users authentication."""

from typing import TYPE_CHECKING, Optional

from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .profile import Profile


class User(SQLAlchemyBaseUserTableUUID, Base):
    """
    User model for authentication using FastAPI-Users.

    Attributes:
        id: UUID primary key
        email: User's email address (unique)
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        is_superuser: Whether the user has admin privileges
        is_verified: Whether the user's email is verified
        profile: Associated profile for this user
    """

    __tablename__ = "users"

    # Override email to add index
    email: Mapped[str] = mapped_column(String(length=320), unique=True, index=True, nullable=False)

    # Relationship to profile (one-to-one)
    profile: Mapped[Optional["Profile"]] = relationship(
        "Profile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}'>"
