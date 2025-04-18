"""
Shared API dependencies for the PillChecker application.

This module provides reusable dependencies for FastAPI route handlers, including:
- Database session management
- Authentication and authorization
- Service access
- Pagination and filtering utilities

These dependencies can be used with FastAPI's dependency injection system:

```python
@router.get("/items")
def read_items(db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    return db.query(models.Item).filter(models.Item.owner_id == user["id"]).all()
```
"""

from functools import lru_cache
from typing import Any, Dict, Generator

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session

from pill_checker.core.database import SessionLocal
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from pill_checker.core.config import get_settings
from pill_checker.services.auth import AuthService

# Settings instance
settings = get_settings()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


# Database dependencies
def get_db() -> Generator[Session, None, None]:
    """
    Create and yield a database session.

    This dependency is used to create a new database session for each request,
    ensuring that the session is properly closed after the request is processed.

    Usage:
        ```python
        @router.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
        ```

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Authentication dependencies
@lru_cache()
def get_auth_service() -> AuthService:
    """
    Get or create an instance of the Auth service.

    This function uses lru_cache to ensure only one instance is created.

    Returns:
        AuthService: Initialized authentication service
    """
    options = ClientOptions(
        postgrest_client_timeout=60,
        storage_client_timeout=120,
        auto_refresh_token=True,
    )

    supabase_client: Client = create_client(
        settings.SUPABASE_URL, settings.SUPABASE_KEY, options=options
    )

    return AuthService(supabase_client)


def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Validate the access token and get the current user.

    This dependency extracts and validates the JWT token from the request,
    then returns the user data if the token is valid.

    Args:
        token: JWT access token from the Authorization header

    Returns:
        dict: User data including id, email, and profile

    Raises:
        HTTPException: 401 error if the token is invalid
    """
    try:
        auth_service = get_auth_service()
        user_data = auth_service.verify_token(token)

        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_data
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_active_user(
    current_user: Dict[str, Any] = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get the current active user.

    This dependency extends get_current_user to check if the user is active.
    It could be extended to check other conditions (e.g., verified email, not banned).

    Args:
        current_user: User data from get_current_user

    Returns:
        dict: User data

    Raises:
        HTTPException: 400 error if the user is inactive
    """
    # Could add additional checks here (e.g., is user active, verified, etc.)
    if current_user.get("disabled"):
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_admin_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """
    Check if the current user is an admin.

    Args:
        current_user: User data from get_current_user

    Returns:
        dict: User data

    Raises:
        HTTPException: 403 error if the user is not an admin
    """
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )
    return current_user


def get_supabase_client() -> Client:
    """
    Get a configured Supabase client instance.

    Returns:
        Client: Initialized Supabase client
    """
    options = ClientOptions(
        postgrest_client_timeout=60,
        storage_client_timeout=120,
        auto_refresh_token=True,
    )

    return create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY, options=options)


# Pagination and filtering dependencies
def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Items per page"),
) -> Dict[str, int]:
    """
    Common pagination parameters for endpoints.

    This dependency converts page and size parameters into skip and limit values
    for database queries.

    Args:
        page: Page number (1-indexed)
        size: Number of items per page

    Returns:
        dict: Dictionary with pagination parameters
    """
    skip = (page - 1) * size
    return {"skip": skip, "limit": size, "page": page, "size": size}
