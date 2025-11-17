"""Authentication manager using FastAPI-Users."""

import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from pill_checker.core.config import settings
from pill_checker.core.logging_config import logger
from pill_checker.models.user import User


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """User manager for handling user operations."""

    reset_password_token_secret = settings.SECRET_KEY
    verification_token_secret = settings.SECRET_KEY

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Hook called after user registration."""
        logger.info(f"User {user.id} has registered with email {user.email}")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Hook called after password reset request."""
        logger.info(f"User {user.id} has requested password reset. Token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        """Hook called after email verification request."""
        logger.info(f"User {user.id} has requested email verification. Token: {token}")


async def get_user_db(db=None):
    """
    Get user database adapter.
    Note: This is imported from dependencies.py in actual usage.
    """
    if db is None:
        from pill_checker.api.v1.dependencies import get_db

        for session in get_db():
            yield SQLAlchemyUserDatabase(session, User)
    else:
        yield SQLAlchemyUserDatabase(db, User)


async def get_user_manager(user_db: SQLAlchemyUserDatabase = Depends(get_user_db)):
    """Get user manager instance."""
    yield UserManager(user_db)


def get_jwt_strategy() -> JWTStrategy:
    """Get JWT authentication strategy."""
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


# Bearer transport for JWT tokens
bearer_transport = BearerTransport(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Authentication backend
auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

# FastAPI Users instance
fastapi_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend],
)

# Dependencies for current user
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
