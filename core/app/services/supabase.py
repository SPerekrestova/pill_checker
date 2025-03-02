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
        self.client = None
        try:
            # Check if required settings are available
            if (
                not settings.SUPABASE_URL
                or not hasattr(settings, "SUPABASE_KEY")
                or not settings.SUPABASE_KEY
            ):
                logger.error("SUPABASE_URL or SUPABASE_KEY not set in environment")
                return

            options = ClientOptions(
                postgrest_client_timeout=60, storage_client_timeout=120, auto_refresh_token=True
            )

            # Use the SUPABASE_URL from settings which is set to http://kong:8000 in the .env file
            # This allows us to access it through the Kong gateway from inside the container
            supabase_url = settings.SUPABASE_URL
            logger.info(f"Initializing Supabase client with URL: {supabase_url}")

            self.client = create_client(supabase_url, settings.SUPABASE_KEY, options=options)

            # Test connection
            try:
                # We won't test auth session, as it might not be initialized yet
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.warning(f"Could not get session (this is normal for first startup): {e}")
                pass

        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.client = None

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
            Optional[ProfileInDB]: Profile data if successful, None on failure
        """
        if self.client is None:
            logger.error("Supabase client not initialized")
            return None

        try:
            # Create auth user with better error handling
            try:
                logger.info(f"Attempting to create user with email: {email}")
                auth_response = self.client.auth.sign_up({"email": email, "password": password})
                logger.info(f"Auth response received: {auth_response}")
            except Exception as auth_err:
                logger.error(f"Error during user creation with Supabase: {auth_err}")
                if "timed out" in str(auth_err):
                    logger.error(
                        "Connection to Supabase timed out. Consider increasing client timeout values."
                    )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"User creation failed: {str(auth_err)}",
                )

            if not auth_response or not auth_response.user:
                logger.error("Auth response did not contain user data")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to create user"
                )

            # Get the user ID from the response
            user_id = auth_response.user.id
            logger.info(f"User created with ID: {user_id}")

            # Create the profile
            profile_data = {
                "id": str(user_id),  # UUID is the primary key now
                "username": username or email.split("@")[0],
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Use the service role directly for profile creation
            try:
                logger.info(f"Attempting to create profile for user {user_id} using service role")
                profile_response = self.client.from_("profiles").insert(profile_data).execute()
                logger.info(f"Profile response received: {profile_response}")
            except Exception as profile_err:
                logger.error(f"Error during profile creation: {profile_err}")
                # Return a basic profile without DB insertion
                return ProfileInDB(
                    id=user_id,
                    username=username or email.split("@")[0],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

            if not profile_response.data:
                logger.warning(
                    f"Failed to create profile for user {user_id}, will return user only"
                )
                # Return a basic profile with just the user information
                return ProfileInDB(
                    id=user_id,
                    username=username or email.split("@")[0],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )

            logger.info(f"Successfully created user and profile for {email}")
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
        if self.client is None:
            logger.error("Supabase client not initialized")
            return None

        try:
            # We need to ensure we have the proper permissions to read the profile
            # If we don't have a session token, we'll use the service role key
            response = (
                self.client.from_("profiles").select("*").eq("id", str(user_id)).single().execute()
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
        if self.client is None:
            logger.error("Supabase client not initialized")
            return None

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
        if self.client is None:
            logger.error("Supabase client not initialized")
            return False

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
        if self.client is None:
            logger.error("Supabase client not initialized")
            return False, None

        try:
            # Better error handling for authentication
            try:
                auth_response = self.client.auth.sign_in_with_password(
                    {"email": email, "password": password}
                )
            except Exception as auth_err:
                logger.error(f"Authentication error with Supabase: {auth_err}")
                return False, None

            if not auth_response or not auth_response.user:
                logger.warning(f"Authentication failed for {email}: No user in response")
                return False, None

            # Get user profile
            profile = None
            try:
                # Use the authenticated role from the session
                if auth_response.session and auth_response.session.access_token:
                    self.client.postgrest.auth(auth_response.session.access_token)

                profile = self.get_user_profile(auth_response.user.id)
                # If profile doesn't exist, try to create it
                if not profile:
                    logger.warning(
                        f"No profile found for user {auth_response.user.id}, attempting to create one"
                    )
                    profile = self.create_profile_for_existing_user(
                        auth_response.user.id, email.split("@")[0]
                    )
            except Exception as profile_err:
                logger.error(f"Error getting/creating profile: {profile_err}")
                profile = None

            # Get session with better error handling
            try:
                session = auth_response.session
                if not session:
                    session = self.client.auth.get_session()
            except Exception as session_err:
                logger.error(f"Error getting session: {session_err}")
                return False, None

            # Return successful authentication result
            return True, {
                "access_token": session.access_token,
                "refresh_token": session.refresh_token,
                "user": {
                    "user_id": auth_response.user.id,
                    "email": auth_response.user.email,
                    "role": auth_response.user.role,  # Include the user's role
                    "profile": profile.model_dump() if profile else None,
                },
            }

        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, None

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify JWT token and get user data."""
        if self.client is None:
            logger.error("Supabase client not initialized")
            return None

        try:
            user_response = self.client.auth.get_user(token)
            if not user_response or not hasattr(user_response, "user") or not user_response.user:
                return None

            # Extract user correctly from the response
            user = user_response.user
            user_id = str(user.id)

            # Get profile for the user
            profile = self.get_user_profile(user_id)

            # Construct user data response
            return {
                "id": user_id,
                "email": user.email,
                "profile": profile.model_dump() if profile else None,
            }
        except Exception as e:
            logger.error(f"Token verification error: {e}")
            return None

    def create_profile_for_existing_user(
        self, user_id: str, username: Optional[str] = None
    ) -> Optional[ProfileInDB]:
        """Create a profile for an existing user."""
        if self.client is None:
            logger.error("Supabase client not initialized")
            return None

        try:
            # First check if profile exists
            existing_profile = (
                self.client.from_("profiles").select("*").eq("id", str(user_id)).single().execute()
            )

            if existing_profile.data:
                # Profile exists, return it
                return ProfileInDB(**existing_profile.data)

            # Create new profile if it doesn't exist
            data = {
                "id": str(user_id),
                "username": username or "User",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Use service role key directly for profile creation
            logger.info("Using service role for profile creation")

            # Insert the profile data
            profile_response = self.client.from_("profiles").insert(data).execute()

            if not profile_response.data:
                logger.error("Failed to create profile")
                return None

            return ProfileInDB(**profile_response.data[0])

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            return None


@lru_cache()
def get_supabase_service() -> SupabaseService:
    """Get or create Supabase service instance."""
    return SupabaseService()
