"""Unified Supabase service for authentication and profile management."""

from functools import lru_cache
from typing import Optional, Tuple, Dict, Any
from uuid import UUID
from datetime import datetime

from fastapi import HTTPException, status
from supabase import create_client
from supabase.lib.client_options import ClientOptions

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.profile import ProfileUpdate, ProfileInDB


class SupabaseService:
    """Unified service for Supabase operations."""

    def __init__(self):
        """Initialize Supabase client with proper configuration."""
        try:
            options = ClientOptions(
                postgrest_client_timeout=10,
                storage_client_timeout=30,
                # Add auth settings to ensure the correct path is used
                auth={"url": "/auth/v1"},
                auto_refresh_token=True
            )

            # The SUPABASE_URL should be http://localhost:8000
            # as we want to access it through the Kong gateway
            self.client = create_client(
                settings.SUPABASE_URL, settings.SUPABASE_KEY, options=options
            )

            # Test connection
            try:
                self.client.auth.get_session()
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.warning(f"Could not get session (this is normal for first startup): {e}")
                pass

        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def create_user_with_profile(
        self, email: str, password: str, username: Optional[str] = None
    ) -> Optional[ProfileInDB]:
        """
        Create a new user and their profile.

        Args:
            email: User's email
            password: User's password
            username: Optional username

        Returns:
            dict: User data and profile data
        """
        try:
            # Create auth user
            auth_response = self.client.auth.sign_up({"email": email, "password": password})

            if not auth_response or not auth_response.user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
                )

            # Get the user ID from the response
            user_id = auth_response.user.id

            # Create the profile
            profile_data = {
                "id": str(user_id),  # UUID is the primary key now
                "username": username or email.split("@")[0],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            self.client.table("profiles").insert(profile_data).execute()

            return self.get_user_profile(user_id)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating user with profile: {e}")
            return None

    def get_user_profile(self, user_id: UUID) -> Optional[ProfileInDB]:
        """
        Get user profile by user ID.

        Args:
            user_id: User's UUID from auth

        Returns:
            Optional[ProfileInDB]: Profile data if found
        """
        try:
            response = (
                self.client.from_("profiles")
                .select("*")
                .eq("id", str(user_id))
                .single()
                .execute()
            )
            return ProfileInDB(**response.data) if response.data else None
        except Exception as e:
            logger.error(f"Error fetching user profile: {e}")
            return None

    def update_user_profile(
        self, user_id: UUID, profile_data: ProfileUpdate
    ) -> Optional[ProfileInDB]:
        """
        Update user profile.

        Args:
            user_id: User's UUID from auth
            profile_data: Profile update data

        Returns:
            Optional[ProfileInDB]: Updated profile data if successful
        """
        try:
            response = (
                self.client.from_("profiles")
                .update(profile_data.model_dump(exclude_unset=True, exclude_none=True))
                .eq("id", str(user_id))
                .execute()
            )

            return ProfileInDB(**response.data[0]) if response.data else None
        except Exception as e:
            logger.error(f"Error updating user profile: {e}")
            return None

    def delete_user_with_profile(self, user_id: UUID) -> bool:
        """Delete user and their profile."""
        try:
            # Delete profile first (due to foreign key constraint)
            (self.client.from_("profiles").delete().eq("id", str(user_id)).execute())

            # Delete auth user
            self.client.auth.admin.delete_user(str(user_id))
            return True
        except Exception as e:
            logger.error(f"Error deleting user with profile: {e}")
            return False

    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authenticate user and return session data."""
        try:
            auth_response = self.client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )

            if not auth_response or not auth_response.user:
                return False, None

            # Get user profile
            profile = self.get_user_profile(auth_response.user.id)

            # Get session
            session = self.client.auth.get_session()

            return True, {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "user": {
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "profile": profile.model_dump() if profile else None,
                },
            }

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify JWT token and return user data.

        Args:
            token: JWT token

        Returns:
            Optional[dict]: User data if token is valid
        """
        try:
            user = self.client.auth.get_user(token)
            if not user:
                return None

            profile = self.get_user_profile(user.id)

            return {
                "user_id": user.id,
                "email": user.email,
                "profile": profile.model_dump() if profile else None,
            }
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def create_profile_for_existing_user(
        self, user_id: str, username: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a profile for an existing user."""
        try:
            # First check if profile exists
            existing_profile = (
                self.client.from_("profiles")
                .select("*")
                .eq("id", str(user_id))
                .single()
                .execute()
            )

            if existing_profile.data:
                # Profile exists, return it
                return existing_profile.data

            # Create new profile if it doesn't exist
            data = {
                "id": str(user_id),
                "username": username or "User",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Get current session
            session = self.client.auth.get_session()

            # Set auth header
            self.client.postgrest.auth(session.access_token)

            profile_response = self.client.table("profiles").insert(data).execute()

            if not profile_response.data:
                logger.error("Failed to create profile")
                return None

            return profile_response.data[0]

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return None


@lru_cache()
def get_supabase_service() -> SupabaseService:
    """Get or create Supabase service instance."""
    return SupabaseService()
