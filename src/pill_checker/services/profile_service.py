"""Profile service for managing user profiles with SQLAlchemy."""

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from pill_checker.core.logging_config import logger
from pill_checker.models.profile import Profile
from pill_checker.models.user import User
from pill_checker.schemas.profile import ProfileUpdate


class ProfileService:
    """Service for managing user profiles."""

    def __init__(self, db: Session):
        """Initialize profile service with database session."""
        self.db = db

    def get_profile_by_user_id(self, user_id: uuid.UUID) -> Optional[Profile]:
        """
        Get profile by user ID.

        Args:
            user_id: User's UUID

        Returns:
            Profile if found, None otherwise
        """
        try:
            profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
            return profile
        except Exception as e:
            logger.error(f"Error fetching profile for user {user_id}: {e}")
            return None

    def get_profile_by_id(self, profile_id: uuid.UUID) -> Optional[Profile]:
        """
        Get profile by profile ID.

        Args:
            profile_id: Profile's UUID

        Returns:
            Profile if found, None otherwise
        """
        try:
            profile = self.db.query(Profile).filter(Profile.id == profile_id).first()
            return profile
        except Exception as e:
            logger.error(f"Error fetching profile {profile_id}: {e}")
            return None

    def create_profile(
        self, user_id: uuid.UUID, username: Optional[str] = None
    ) -> Optional[Profile]:
        """
        Create a new profile for a user.

        Args:
            user_id: User's UUID
            username: Optional username

        Returns:
            Created Profile or None if creation failed
        """
        try:
            # Check if profile already exists
            existing_profile = self.get_profile_by_user_id(user_id)
            if existing_profile:
                logger.warning(f"Profile already exists for user {user_id}")
                return existing_profile

            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                logger.error(f"User {user_id} not found")
                return None

            # Create new profile
            profile = Profile(
                user_id=user_id,
                username=username or user.email.split("@")[0],
            )

            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Profile created for user {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error creating profile for user {user_id}: {e}")
            self.db.rollback()
            return None

    def update_profile(
        self, user_id: uuid.UUID, profile_data: ProfileUpdate
    ) -> Optional[Profile]:
        """
        Update user profile.

        Args:
            user_id: User's UUID
            profile_data: Profile update data

        Returns:
            Updated Profile or None if update failed
        """
        try:
            profile = self.get_profile_by_user_id(user_id)
            if not profile:
                logger.warning(f"Profile not found for user {user_id}")
                return None

            # Update fields
            update_data = profile_data.model_dump(exclude_unset=True, exclude_none=True)
            for field, value in update_data.items():
                setattr(profile, field, value)

            self.db.commit()
            self.db.refresh(profile)

            logger.info(f"Profile updated for user {user_id}")
            return profile

        except Exception as e:
            logger.error(f"Error updating profile for user {user_id}: {e}")
            self.db.rollback()
            return None

    def delete_profile(self, user_id: uuid.UUID) -> bool:
        """
        Delete user profile.

        Args:
            user_id: User's UUID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            profile = self.get_profile_by_user_id(user_id)
            if not profile:
                logger.warning(f"Profile not found for user {user_id}")
                return False

            self.db.delete(profile)
            self.db.commit()

            logger.info(f"Profile deleted for user {user_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting profile for user {user_id}: {e}")
            self.db.rollback()
            return False


def get_profile_service(db: Session) -> ProfileService:
    """Get profile service instance."""
    return ProfileService(db)
