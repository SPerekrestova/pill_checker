"""Tests for authentication service and endpoints."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.auth import router as auth_router
from app.core.security import setup_security
from app.services.supabase import SupabaseService

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"
TEST_USER_ID = str(uuid.uuid4())
TEST_DISPLAY_NAME = "Test User"


@pytest.fixture
def mock_supabase_service():
    """Mock Supabase service."""
    with patch("app.api.v1.auth.get_supabase_service") as mock:
        service = AsyncMock(spec=SupabaseService)
        service.create_user_with_profile = AsyncMock()
        service.authenticate_user = AsyncMock()

        # Mock auth client
        auth = AsyncMock()
        auth.sign_out = AsyncMock()
        auth.refresh_session = AsyncMock()
        auth.reset_password_email = AsyncMock()
        auth.verify_otp = AsyncMock()
        auth.update_user = AsyncMock()

        # Mock client
        client = AsyncMock()
        client.auth = auth
        service.client = client

        mock.return_value = service
        yield service


@pytest.fixture
def test_app(mock_supabase_service):
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

    def test_register_success(self, test_client, mock_supabase_service):
        """Test successful user registration."""
        # Mock successful user creation
        mock_supabase_service.create_user_with_profile.return_value = {"user_id": TEST_USER_ID}

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
        assert response.json()["user_id"] == TEST_USER_ID
        mock_supabase_service.create_user_with_profile.assert_called_once_with(
            email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD, username=TEST_DISPLAY_NAME
        )

    def test_register_password_mismatch(self, test_client):
        """Test registration with mismatched passwords."""
        response = test_client.post(
            "/api/v1/auth/register",
            json={
                "email": TEST_USER_EMAIL,
                "password": TEST_USER_PASSWORD,
                "password_confirm": "different_password",
                "display_name": TEST_DISPLAY_NAME,
            },
        )

        assert response.status_code == 400
        assert "Passwords do not match" in response.json()["detail"]

    def test_login_success(self, test_client, mock_supabase_service):
        """Test successful login."""
        # Mock successful authentication
        mock_supabase_service.authenticate_user.return_value = {
            "access_token": "test_access_token",
            "refresh_token": "test_refresh_token",
        }

        response = test_client.post(
            "/api/v1/auth/login", data={"username": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "test_access_token"
        assert response.json()["refresh_token"] == "test_refresh_token"
        mock_supabase_service.authenticate_user.assert_called_once_with(
            email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD
        )

    def test_login_failure(self, test_client, mock_supabase_service):
        """Test login with invalid credentials."""
        # Mock failed authentication
        mock_supabase_service.authenticate_user.side_effect = Exception("Invalid credentials")

        response = test_client.post(
            "/api/v1/auth/login", data={"username": TEST_USER_EMAIL, "password": "wrong_password"}
        )

        assert response.status_code == 401
        assert "Incorrect email or password" in response.json()["detail"]

    def test_logout(self, test_client, mock_supabase_service):
        """Test logout endpoint."""
        response = test_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"
        mock_supabase_service.client.auth.sign_out.assert_called_once()

    def test_refresh_token_success(self, test_client, mock_supabase_service):
        """Test successful token refresh."""
        # Mock successful token refresh
        mock_session = MagicMock()
        mock_session.access_token = "new_access_token"
        mock_session.refresh_token = "new_refresh_token"
        mock_response = AsyncMock()
        mock_response.session = mock_session
        mock_supabase_service.client.auth.refresh_session.return_value = mock_response

        response = test_client.post(
            "/api/v1/auth/refresh-token", json={"refresh_token": "old_refresh_token"}
        )

        assert response.status_code == 200
        assert response.json()["access_token"] == "new_access_token"
        assert response.json()["refresh_token"] == "new_refresh_token"

    def test_refresh_token_failure(self, test_client, mock_supabase_service):
        """Test token refresh with invalid token."""
        # Mock failed token refresh
        mock_supabase_service.client.auth.refresh_session.return_value = None

        response = test_client.post(
            "/api/v1/auth/refresh-token", json={"refresh_token": "invalid_token"}
        )

        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_password_reset_request(self, test_client, mock_supabase_service):
        """Test password reset request."""
        response = test_client.post(
            "/api/v1/auth/password-reset/request", json={"email": TEST_USER_EMAIL}
        )

        assert response.status_code == 200
        assert "password reset" in response.json()["message"].lower()
        mock_supabase_service.client.auth.reset_password_email.assert_called_once_with(
            TEST_USER_EMAIL
        )

    def test_verify_email(self, test_client, mock_supabase_service):
        """Test email verification."""
        # Mock successful verification
        mock_supabase_service.client.auth.verify_otp.return_value = True

        response = test_client.get("/api/v1/auth/verify-email", params={"token": "test_token"})

        assert response.status_code == 200
        assert "successfully verified" in response.json()["message"].lower()
        mock_supabase_service.client.auth.verify_otp.assert_called_once_with(
            "test_token", type_="email"
        )
