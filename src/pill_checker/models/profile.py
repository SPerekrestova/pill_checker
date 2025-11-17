import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import CheckConstraint, Column, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .medication import Medication
    from .user import User


class Profile(Base):
    """
    Model for user profiles.

    Attributes:
        id: UUID primary key
        user_id: UUID of the associated user (foreign key)
        username: Username of the user (unique)
        bio: User's biography or description
        user: Associated user account
        medications: List of medications associated with this profile
    """

    __tablename__ = "profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Profile UUID",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="UUID of the associated user",
    )
    username: Mapped[Optional[str]] = Column(
        Text, nullable=True, unique=True, comment="Display name of the user"
    )
    bio: Mapped[Optional[str]] = Column(
        Text, nullable=True, comment="User's biography or description"
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="profile")
    medications: Mapped[List["Medication"]] = relationship(
        "Medication", back_populates="profile", cascade="all, delete-orphan"
    )

    # Constraints and Indexes
    __table_args__ = (
        CheckConstraint("char_length(username) >= 3", name="username_length"),
        Index("idx_profile_display_name", "username"),
        Index("idx_profile_user_id", "user_id", unique=True),
    )

    def __repr__(self) -> str:
        return f"<Profile id={self.id} username='{self.username}' user_id={self.user_id}>"
