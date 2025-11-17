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

from typing import Any, Dict, Generator

from fastapi import Depends, Query
from fastapi_users.db import SQLAlchemyUserDatabase
from sqlalchemy.orm import Session

from pill_checker.core.config import get_settings
from pill_checker.core.database import SessionLocal
from pill_checker.models.user import User

# Settings instance
settings = get_settings()


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


# User database dependency
async def get_user_db(db: Session = Depends(get_db)) -> SQLAlchemyUserDatabase:
    """
    Get user database adapter for FastAPI-Users.

    Args:
        db: Database session

    Yields:
        SQLAlchemyUserDatabase: User database adapter
    """
    yield SQLAlchemyUserDatabase(db, User)


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
