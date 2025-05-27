"""Tests for authentication service and endpoints."""

import uuid
from unittest.mock import MagicMock, Mock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pill_checker.api.v1.auth import router as auth_router
from pill_checker.core.security import setup_security
from pill_checker.schemas.profile import ProfileInDB
from pill_checker.services.auth import AuthService

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_ID = str(uuid.uuid4())
TEST_DISPLAY_NAME = "Test User"


@pytest.fixture
def mock_auth_service():
    """Mock Auth service with proper return values."""
    with patch("pill_checker.api.v1.auth.get_auth_service") as mock_get_service:
        # Create a properly configured mock service
        service = MagicMock(spec=AuthService)

        # Create a proper ProfileInDB object for create_user_with_profile
        profile = ProfileInDB(
            id=TEST_USER_ID,
            username=TEST_DISPLAY_NAME,
            created_at="2023-01-01T00:00:00",
            updated_at="2023-01-01T00:00:00",
        )
        service.create_user_with_profile.return_value = profile

        # Mock authenticate_user to return proper values
        service.authenticate_user.return_value = (
            True,
            {
                "access_token": "test_access_token",
                "refresh_token": "test_refresh_token",
                "user": {
                    "user_id": TEST_USER_ID,
                    "email": TEST_USER_EMAIL,
                    "role": "user",
                    "profile": {"id": TEST_USER_ID, "username": TEST_DISPLAY_NAME},
                },
            },
        )

        # Mock refresh_session to return proper values
        service.refresh_session.return_value = {
            "access_token": "new_access_token",
            "refresh_token": "new_refresh_token",
        }

        # Configure the mock supabase client
        mock_supabase = MagicMock()
        service.supabase = mock_supabase

        # Return the service when get_auth_service is called
        mock_get_service.return_value = service

        yield service


@pytest.fixture
def test_app(mock_auth_service):
    """Create test FastAPI application."""
    app = FastAPI()
    setup_security(app)
    app.include_router(auth_router, prefix="/api/v1/auth")
    return app


@pytest.fixture
def test_client(test_app):
    """Create test client."""
    return TestClient(test_app)


class TestAuthEndpoints:
    """Test suite for authentication endpoints."""

    def test_register_success(self, test_client, mock_auth_service):
        """Test successful user registration."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "password_confirm": TEST_USER_PASSWORD,
                "username": TEST_DISPLAY_NAME,
            },
        )

        assert response.status_code == 201
        assert "user_id" in response.json()
        assert response.json()["user_id"] == TEST_USER_ID
        mock_auth_service.create_user_with_profile.assert_called_once_with(
            email=TEST_USER_EMAIL,
            password=TEST_USER_PASSWORD,
            username=TEST_DISPLAY_NAME,
        )

    def test_register_password_mismatch(self, test_client):
        """Test registration with mismatched passwords."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "password_confirm": "different_password",
                "username": TEST_DISPLAY_NAME,
            },
        )

        assert response.status_code == 400
        assert "Passwords do not match" in response.json()["detail"]

    def test_login_success(self, test_client, mock_auth_service):
        """Test successful login."""
        response = test_client.post(
            "/api/v1/auth/login",
            data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD},
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "test_access_token"
        assert response.json()["refresh_token"] == "test_refresh_token"
        assert response.json()["token_type"] == "bearer"
        mock_auth_service.authenticate_user.assert_called_once_with(
            email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD
        )

    def test_login_failure(self, test_client, mock_auth_service):
        """Test login with invalid credentials."""
        # Mock failed authentication
        mock_auth_service.authenticate_user.return_value = (False, None)

        response = test_client.post(
            "/api/v1/auth/login",
            data={"username": TEST_USER_EMAIL, "password": "wrong_password"},
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_logout(self, test_client, mock_auth_service):
        """Test logout endpoint."""
        response = test_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_refresh_token_success(self, test_client, mock_auth_service):
        """Test successful token refresh."""
        response = test_client.post(
            "/api/v1/auth/refresh-token", json={"refresh_token": "old_refresh_token"}
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "new_access_token"
        assert response.json()["refresh_token"] == "new_refresh_token"
        assert response.json()["token_type"] == "bearer"
        # The token property is used internally
        mock_auth_service.refresh_session.assert_called_once()

    def test_refresh_token_failure(self, test_client, mock_auth_service):
        """Test token refresh with invalid token."""
        # Mock failed token refresh - raise exception
        mock_auth_service.refresh_session.side_effect = Exception("Invalid token")

        response = test_client.post(
            "/api/v1/auth/refresh-token", json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]
