from django.http import HttpRequest, HttpResponseRedirect
from django.contrib.auth.models import AnonymousUser
from MedsRecognition.medication_views import user_dashboard
import django
import os
import unittest
from unittest.mock import patch, MagicMock

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MedsRecognition.settings")

django.setup()


class TestUserDashboard(unittest.TestCase):
    @patch("MedsRecognition.medication_views.render")
    @patch("MedsRecognition.medication_views.ScannedMedication.objects.filter")
    @patch("MedsRecognition.decorators.Profile.objects.get")
    def test_user_dashboard_authenticated_user(self, mock_profile_get, mock_filter, mock_render):
        mock_request = MagicMock(spec=HttpRequest)
        mock_request.session = {"supabase_user": "123e4567-e89b-12d3-a456-426614174000"}

        mock_profile = MagicMock()
        mock_profile_get.return_value = mock_profile

        mock_request.auth_user = mock_profile

        mock_medication = MagicMock()
        mocked_queryset = MagicMock()
        mocked_queryset.order_by = MagicMock(return_value=[mock_medication])
        mock_filter.return_value = mocked_queryset

        user_dashboard(mock_request)

        mock_profile_get.assert_called_once_with(user_id="123e4567-e89b-12d3-a456-426614174000")

        mock_filter.assert_called_once_with(profile=mock_profile)
        mock_render.assert_called_once_with(
            mock_request,
            "recognition/dashboard.html",
            {"medications": [mock_medication]},
        )

    @patch("django.shortcuts.redirect")
    def test_user_dashboard_anonymous_user_redirects_to_login(self, mock_redirect):
        # Mock request with an empty session (no 'supabase_user')
        mock_request = MagicMock(spec=HttpRequest)
        mock_request.auth_user = AnonymousUser()
        mock_request.session = {}  # No 'supabase_user' in session

        mock_redirect.return_value = HttpResponseRedirect("login")

        response = user_dashboard(mock_request)

        # Ensure the decorator triggered a redirect to "login"
        assert isinstance(response, HttpResponseRedirect)
        assert response.url == "/login/"
