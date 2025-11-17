"""Authentication dependencies for FastAPI routes using FastAPI-Users."""

from fastapi import Depends

from pill_checker.models.user import User
from pill_checker.services.auth_manager import current_active_user


async def get_current_user(user: User = Depends(current_active_user)) -> dict:
    """
    Get current authenticated user.

    Returns a dictionary for backward compatibility with existing code.
    """
    return {
        "id": str(user.id),
        "email": user.email,
        "is_active": user.is_active,
        "is_superuser": user.is_superuser,
    }
