"""API v1 endpoints."""

from .auth import router as auth_router
from .medications import router as medications_router

__all__ = ["auth_router", "medications_router"]
