import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, Column, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, relationship

from .base import Base

if TYPE_CHECKING:
    from .medication import Medication


class Profile(Base):
    """
    Model for user profiles.

    Attributes:
        id: UUID of the associated Supabase user (primary key)
        username: Username of the user (unique)
        bio: User's biography or description
        medications: List of medications associated with this profile
    """

    __tablename__ = "profiles"  # Use plural form for table names

    id: Mapped[uuid.UUID] = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="UUID of the associated Supabase user",
    )
    username: Mapped[Optional[str]] = Column(
        Text, nullable=True, unique=True, comment="Display name of the user"
    )
    bio: Mapped[Optional[str]] = Column(
        Text, nullable=True, comment="User's biography or description"
    )

    # Relationships
    medications: Mapped[List["Medication"]] = relationship(
        "Medication", back_populates="profile", cascade="all, delete-orphan"
    )

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("char_length(username) >= 3", name="username_length"),
        Index("idx_profile_display_name", "username"),
        Index("ix_profile_user_id", "id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Profile id={self.id} username='{self.username}'>"
