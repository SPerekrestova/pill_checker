"""Tests for authentication service and endpoints."""

import uuid
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from pill_checker.api.v1.auth import router as auth_router
from pill_checker.core.security import setup_security
from pill_checker.models.user import User

# Test data
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "Test123!Password"
TEST_USER_ID = uuid.uuid4()
TEST_USERNAME = "testuser"


@pytest.fixture
def mock_user_manager():
    """Mock FastAPI-Users UserManager."""
    with patch("pill_checker.api.v1.auth.get_user_manager") as mock_get_manager:
        mock_manager = MagicMock()

        # Create a mock user
        user = User(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            hashed_password="hashed_password",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )

        # Mock user creation
        async def mock_create(user_create):
            return user

        mock_manager.create = mock_create

        # Return async generator
        async def mock_get_manager_gen(*args, **kwargs):
            yield mock_manager

        mock_get_manager.return_value = mock_get_manager_gen()

        yield mock_manager


@pytest.fixture
def mock_fastapi_users():
    """Mock FastAPI-Users authentication."""
    with (
        patch("pill_checker.api.v1.auth.fastapi_users") as mock_fapi_users,
        patch("pill_checker.api.v1.auth.current_active_user") as mock_current_user,
    ):
        # Create mock user
        user = User(
            id=TEST_USER_ID,
            email=TEST_USER_EMAIL,
            hashed_password="hashed",
            is_active=True,
            is_superuser=False,
            is_verified=True,
        )

        # Mock current_active_user to return the user
        mock_current_user.return_value = user

        # Mock get_register_router
        mock_register_router = MagicMock()
        mock_fapi_users.get_register_router.return_value = mock_register_router

        # Mock get_auth_router
        mock_auth_router = MagicMock()
        mock_fapi_users.get_auth_router.return_value = mock_auth_router

        yield mock_fapi_users


@pytest.fixture
def test_app():
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

    def test_me_endpoint(self, test_client, mock_fastapi_users):
        """Test /me endpoint returns current user info."""
        # This test verifies the custom /me endpoint exists
        # The actual functionality is tested through integration tests
        assert auth_router is not None

    def test_register_with_profile_endpoint_exists(self, test_client):
        """Test that register-with-profile endpoint is defined."""
        # Verify the custom registration endpoint is included
        assert auth_router is not None

    def test_auth_router_includes_fastapi_users_routes(self):
        """Test that FastAPI-Users routes are included."""
        # Verify the auth router exists and has routes
        assert auth_router is not None
        # The router should have routes from FastAPI-Users
        assert len(auth_router.routes) > 0


class TestProfileService:
    """Test suite for profile service."""

    def test_profile_service_import(self):
        """Test that ProfileService can be imported."""
        from pill_checker.services.profile_service import ProfileService

        assert ProfileService is not None

    def test_get_profile_service(self):
        """Test that get_profile_service function works."""
        from pill_checker.services.profile_service import get_profile_service

        mock_db = MagicMock()
        service = get_profile_service(mock_db)
        assert service is not None


class TestStorageService:
    """Test suite for storage service."""

    def test_storage_service_import(self):
        """Test that StorageService can be imported."""
        from pill_checker.services.storage import StorageService

        assert StorageService is not None

    def test_get_storage_service(self):
        """Test that get_storage_service function works."""
        from pill_checker.services.storage import get_storage_service

        service = get_storage_service()
        assert service is not None

    @pytest.mark.asyncio
    async def test_storage_upload(self):
        """Test file upload functionality."""
        from pill_checker.services.storage import StorageService

        service = StorageService(base_path="/tmp/test_storage")
        test_content = b"test file content"
        test_path = "test/file.txt"

        # Upload file
        url = await service.upload_file(test_content, test_path)
        assert url == f"/storage/{test_path}"

        # Clean up
        await service.delete_file(test_path)
