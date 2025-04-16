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

from datetime import datetime
from functools import lru_cache
from typing import Any, Callable, Dict, Generator, List, Optional, Union

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from supabase import Client, create_client
from supabase.lib.client_options import ClientOptions

from pill_checker.core.config import get_settings
from pill_checker.db.session import SessionLocal
from pill_checker.services.auth import AuthService
from pill_checker.services.ocr import OCRClient, get_ocr_client
from pill_checker.services.medication import MedicationService

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
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=options
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


def get_current_active_user(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
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


# Service dependencies
def get_ocr_service() -> OCRClient:
    """
    Get an instance of the OCR service.

    Returns:
        OCRClient: OCR service for text extraction
    """
    return get_ocr_client()


def get_medication_service(db: Session = Depends(get_db)) -> MedicationService:
    """
    Get an instance of the Medication service.

    Args:
        db: Database session from get_db

    Returns:
        MedicationService: Service for medication operations
    """
    return MedicationService(db)


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

    return create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY,
        options=options
    )


# Pagination and filtering dependencies
def pagination_params(
        page: int = Query(1, ge=1, description="Page number"),
        size: int = Query(10, ge=1, le=100, description="Items per page")
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


def medication_filters(
        title: Optional[str] = Query(None, description="Filter by medication title"),
        ingredient: Optional[str] = Query(None, description="Filter by active ingredient"),
        start_date: Optional[datetime] = Query(None, description="Filter medications from this date"),
        end_date: Optional[datetime] = Query(None, description="Filter medications until this date"),
        sort_by: Optional[str] = Query("scan_date", description="Sort field (title, scan_date)"),
        sort_order: Optional[str] = Query("desc", description="Sort order (asc, desc)")
) -> Dict[str, Any]:
    """
    Filter and sort parameters for medication queries.

    Args:
        title: Filter by medication title (partial match)
        ingredient: Filter by active ingredient (partial match)
        start_date: Filter medications scanned on or after this date
        end_date: Filter medications scanned on or before this date
        sort_by: Field to sort by
        sort_order: Sort direction (asc or desc)

    Returns:
        dict: Dictionary with filter and sort parameters
    """
    filters = {}

    # Apply text filters if provided
    if title:
        filters["title"] = title
    if ingredient:
        filters["ingredient"] = ingredient

    # Apply date filters if provided
    if start_date:
        filters["start_date"] = start_date
    if end_date:
        filters["end_date"] = end_date

    # Apply sorting
    if sort_by not in ["title", "scan_date", "created_at"]:
        sort_by = "scan_date"  # Default sort field

    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"  # Default sort order

    filters["sort_by"] = sort_by
    filters["sort_order"] = sort_order

    return filters


# Rate limiting dependency
def rate_limit(
        name: str = "default",
        limit: int = 100,
        period: int = 60,  # seconds
) -> Callable:
    """
    Rate limiting dependency factory.

    Creates a dependency that limits the number of requests a user can make
    in a given time period.

    Args:
        name: Unique name for this rate limit
        limit: Maximum number of requests allowed
        period: Time period in seconds

    Returns:
        Callable: Dependency function for rate limiting
    """

    # This is a placeholder for a real implementation
    # In a real app, you'd use redis or another backend to track requests
    async def check_rate_limit(user: Dict[str, Any] = Depends(get_current_user)):
        # In a real implementation, you would:
        # 1. Get the current count for this user and rate limit
        # 2. Increment the count
        # 3. Set expiry for the counter
        # 4. Check if the limit is exceeded
        user_id = user["id"]
        key = f"rate_limit:{name}:{user_id}"

        # If using Redis, you'd do something like:
        # current = await redis.get(key) or 0
        # await redis.incr(key)
        # await redis.expire(key, period)
        # if int(current) >= limit:
        #     raise HTTPException(429, "Rate limit exceeded")

        return user

    return check_rate_limit