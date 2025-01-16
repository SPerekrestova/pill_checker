import pytest

from MedsRecognition.auth_service import sign_up_user
from MedsRecognition.models import Profile


@pytest.fixture(scope="function")
def supabase_test_user(db):
    """
    Create a test Supabase user and corresponding Django Profile.
    Uses the same approach as your supabase_signup_view.
    """
    # Set test credentials and username
    email = "testuser@example.com"
    password = "TestSecurePassword123!"
    username = "testuser"  # Or use email, depending on your view logic

    # Call the Supabase sign-up service (adjust if your parameters differ)
    result = sign_up_user(email=email, password=password)

    # Check the result; adjust based on your actual response structure.
    if not (result and getattr(result, "user", None)):
        pytest.fail("Supabase sign-up failed; cannot create test user.")

    profile, created = Profile.objects.get_or_create(
        user_id=result.user.id,
        defaults={"display_name": username}
    )
    return profile