import json
from unittest.mock import patch, MagicMock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

class SupabaseAuthTests(TestCase):
    def setUp(self):
        self.client = Client()

    @patch("MedsRecognition.views.supabase")
    def test_signup_view(self, mock_supabase):
        # Mock the supabase.auth.sign_up call
        mock_response = MagicMock()
        mock_response.user = MagicMock(id="supabase-uid-123")
        mock_supabase.auth.sign_up.return_value = mock_response

        # Post signup data
        response = self.client.post(reverse('signup'), {
            'email': 'test@example.com',
            'password': 'password123',
            'username': 'testuser'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(email='test@example.com').exists())

        user = User.objects.get(email='test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.supabase_user_id, 'supabase-uid-123')

        # The user should also be logged in
        self.assertIn('_auth_user_id', self.client.session)

    @patch("MedsRecognition.supabase_utils.get_supabase_client")
    def test_login_view(self, mock_supabase):
        # Create a local user that matches the supabase user
        user = User.objects.create(
            email='test@example.com',
            username='testuser',
            supabase_user_id='supabase-uid-123'
        )
        user.set_password('password123')
        user.save()

        # Mock the supabase.auth.sign_in_with_password call
        mock_response = MagicMock()
        mock_response.user = MagicMock(id='supabase-uid-123')
        mock_supabase.auth.sign_in_with_password.return_value = mock_response

        # Attempt to login
        response = self.client.post(reverse('login'), {
            'email': 'test@example.com',
            'password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # User should now be authenticated
        self.assertIn('_auth_user_id', self.client.session)

    @patch("MedsRecognition.supabase_utils.get_supabase_client")
    def test_login_view_no_local_user(self, mock_supabase):
        """
        Test scenario: user is in Supabase but doesn't exist locally.
        The view should show an error and not log in the user.
        """
        mock_response = MagicMock()
        mock_response.user = MagicMock(id='supabase-uid-999')
        mock_supabase.auth.sign_in_with_password.return_value = mock_response

        response = self.client.post(reverse('login'), {
            'email': 'nolocal@example.com',
            'password': 'password123'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        # Should show an error message about no local user
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertContains(response, "No local user found")