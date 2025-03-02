"""Authentication dependencies for FastAPI routes."""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.services.supabase import get_supabase_service

# Main OAuth2 scheme for required authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", scheme_name="JWT")

# Optional OAuth2 scheme that doesn't auto-error
optional_oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login", scheme_name="JWT", auto_error=False
)


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user.

    Args:
        token: JWT token from request

    Returns:
        dict: User data with profile

    Raises:
        HTTPException: If token is invalid
    """
    supabase = get_supabase_service()
    # verify_token is not an async method
    user_data = supabase.verify_token(token)

    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user_data


async def get_optional_user(token: Optional[str] = Depends(optional_oauth2_scheme)):
    """
    Get current user if authenticated, otherwise None.

    Args:
        token: Optional JWT token

    Returns:
        Optional[dict]: User data with profile or None
    """
    if not token:
        return None

    try:
        return await get_current_user(token)
    except HTTPException:
        return None


async def require_profile(user_data: dict = Depends(get_current_user)):
    """
    Ensure user has a profile.

    Args:
        user_data: User data from get_current_user

    Returns:
        dict: User data with profile

    Raises:
        HTTPException: If user has no profile
    """
    if not user_data.get("profile"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User profile not found"
        )
    return user_data
