"""Authentication endpoints using FastAPI-Users."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from pill_checker.api.v1.dependencies import get_db
from pill_checker.core.logging_config import logger
from pill_checker.models.user import User
from pill_checker.schemas.user import UserCreate, UserRead, UserUpdate
from pill_checker.services.auth_manager import auth_backend, fastapi_users, current_active_user
from pill_checker.services.profile_service import ProfileService

# Create router
router = APIRouter()

# Include FastAPI-Users authentication routes
# Register endpoint
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    tags=["auth"],
)

# Login/logout endpoints
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
    tags=["auth"],
)

# Reset password endpoints
router.include_router(
    fastapi_users.get_reset_password_router(),
    tags=["auth"],
)

# Verify email endpoints
router.include_router(
    fastapi_users.get_verify_router(UserRead),
    tags=["auth"],
)

# User management endpoints
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@router.post("/register-with-profile", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register_with_profile(
    user_create: UserCreate,
    db: Session = Depends(get_db),
):
    """
    Register a new user and automatically create their profile.

    This is a custom endpoint that extends the default registration
    to automatically create a user profile.
    """
    try:
        # Use FastAPI-Users to register the user
        from pill_checker.services.auth_manager import get_user_db, get_user_manager

        user_db_gen = get_user_db(db)
        user_db = await user_db_gen.__anext__()

        user_manager_gen = get_user_manager(user_db)
        user_manager = await user_manager_gen.__anext__()

        # Create user
        user = await user_manager.create(user_create)

        # Create profile
        profile_service = ProfileService(db)
        username = user_create.username if hasattr(user_create, 'username') else None
        profile = profile_service.create_profile(user.id, username)

        if not profile:
            logger.warning(f"Profile creation failed for user {user.id}")

        return UserRead.model_validate(user)

    except Exception as e:
        logger.error(f"Registration with profile error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/me", response_model=UserRead)
async def get_current_user_info(
    user: User = Depends(current_active_user),
):
    """Get current user information."""
    return UserRead.model_validate(user)
