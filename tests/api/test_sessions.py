"""Tests for session management."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from pill_checker.core.security import setup_security
from pill_checker.models.user import User
from pill_checker.services.session_service import get_current_user

# Test data
TEST_TOKEN = "test_token"
TEST_USER_ID = uuid.uuid4()
TEST_USER_EMAIL = "test@example.com"


@pytest.fixture
def mock_user():
    """Create a mock user."""
    return User(
        id=TEST_USER_ID,
        email=TEST_USER_EMAIL,
        hashed_password="hashed",
        is_active=True,
        is_superuser=False,
        is_verified=True,
    )


@pytest.fixture
def mock_current_active_user(mock_user):
    """Mock current_active_user dependency."""
    with patch("pill_checker.services.session_service.current_active_user") as mock_current:
        mock_current.return_value = mock_user
        yield mock_current


@pytest.fixture
def test_app():
    """Create test FastAPI application with test routes."""
    app = FastAPI()
    setup_security(app)

    @app.get("/test/protected")
    async def protected_route(user_dict=Depends(get_current_user)):
        return {"user": user_dict}

    return app


@pytest.fixture
def test_client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestSessionManagement:
    """Test suite for session management."""

    def test_protected_route_with_valid_token(self, test_client, mock_current_active_user, mock_user):
        """Test accessing protected route with valid token."""
        response = test_client.get(
            "/test/protected", headers={"Authorization": f"Bearer {TEST_TOKEN}"}
        )

        assert response.status_code == 200
        user_data = response.json()["user"]
        assert user_data["id"] == str(TEST_USER_ID)
        assert user_data["email"] == TEST_USER_EMAIL

    def test_protected_route_without_token(self, test_client):
        """Test accessing protected route without token."""
        response = test_client.get("/test/protected")
        assert response.status_code in [401, 403]  # Depends on FastAPI-Users configuration

    def test_get_current_user_returns_dict(self, mock_user):
        """Test that get_current_user returns a dictionary for backward compatibility."""
        from pill_checker.services.session_service import get_current_user

        # Mock the dependency
        with patch("pill_checker.services.session_service.current_active_user", return_value=mock_user):
            # Create a mock async function to test
            import asyncio

            async def test_func():
                user_dict = await get_current_user(mock_user)
                assert isinstance(user_dict, dict)
                assert user_dict["id"] == str(TEST_USER_ID)
                assert user_dict["email"] == TEST_USER_EMAIL
                assert user_dict["is_active"] is True

            asyncio.run(test_func())
