from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse

class SupabaseAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("MedsRecognition.views.sign_up_user")
    def test_signup_view(self, mock_sign_up_user):
        # Mock the supabase.auth.sign_up call
        mock_response = MagicMock()
        mock_response.user = {'id': "supabase-uid-123"}
        mock_sign_up_user.return_value = mock_response

        # Post signup data
        response = self.client.post(reverse('signup'), {
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Verify that the user is redirected to the login page
        self.assertRedirects(response, reverse('login'))

    @patch("MedsRecognition.views.sign_in_user")
    def test_login_view(self, mock_sign_in_user):
        # Mock the supabase.auth.sign_in_with_password call
        mock_response = MagicMock()
        mock_response.user = {'id': 'supabase-uid-123'}
        mock_sign_in_user.return_value = mock_response

        # Attempt to login
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Verify that the user is redirected to the dashboard
        self.assertRedirects(response, reverse('dashboard'))
        # User should now be authenticated
        self.assertIn('supabase_user', self.client.session)

    @patch("MedsRecognition.views.sign_in_user")
    def test_login_view_no_local_user(self, mock_sign_in_user):
        """
        Test scenario: user is in Supabase but doesn't exist locally.
        The view should show an error and not log in the user.
        """
        mock_response = MagicMock()
        mock_response.user = {'id': 'supabase-uid-999'}
        mock_sign_in_user.return_value = mock_response

        response = self.client.post(reverse('login'), {
            'email': 'nolocal@example.com',
            'password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Should show an error message about no local user
        self.assertNotIn('supabase_user', self.client.session)
        self.assertContains(response, "Invalid credentials or login failed.")