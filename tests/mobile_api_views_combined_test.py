import unittest
from unittest.mock import patch, MagicMock

from django.http import HttpRequest
from django.test import RequestFactory
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIRequestFactory

from MedsRecognition.mobile_api_views import GetUserView
from MedsRecognition.mobile_api_views import UserSignInView
from MedsRecognition.mobile_api_views import UserSignOutView


class TestUserSignInView(unittest.TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("MedsRecognition.mobile_api_views.sign_in_user")
    @patch("MedsRecognition.mobile_api_views.Profile.objects.get_or_create")
    def test_user_sign_in_view_valid_credentials(self, mock_get_or_create, mock_sign_in_user):
        mock_request = self.factory.post(
            "/signin", {"email": "test@example.com", "password": "password123"}
        )
        mock_request.data = {"email": "test@example.com", "password": "password123"}

        mock_result = MagicMock()
        mock_result.user.id = 1
        mock_result.session.access_token = "fake_token"
        mock_sign_in_user.return_value = mock_result
        mock_get_or_create.return_value = (MagicMock(), True)

        response = UserSignInView().post(mock_request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"token": "fake_token"})
        mock_sign_in_user.assert_called_once_with("test@example.com", "password123")
        mock_get_or_create.assert_called_once_with(
            user_id=1, defaults={"display_name": "test@example.com"}
        )

    @patch("MedsRecognition.mobile_api_views.sign_in_user")
    def test_user_sign_in_view_invalid_credentials(self, mock_sign_in_user):
        mock_request = self.factory.post(
            "/signin", {"email": "test@example.com", "password": "wrong_password"}
        )
        mock_request.data = {"email": "test@example.com", "password": "wrong_password"}

        mock_sign_in_user.return_value = None

        response = UserSignInView().post(mock_request)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data, {"error": "Invalid credentials"})
        mock_sign_in_user.assert_called_once_with("test@example.com", "wrong_password")


class TestUserSignOutView(unittest.TestCase):
    @patch("MedsRecognition.mobile_api_views.logout")
    def test_user_sign_out_success(self, mock_logout):
        # Mock request
        mock_request = MagicMock(spec=HttpRequest)

        # Instantiate the view
        view = UserSignOutView()

        # Call the `post` method
        response = view.post(mock_request)

        # Assert that `logout` was called with the request
        mock_logout.assert_called_once_with(mock_request)

        # Assert the correct response
        self.assertIsInstance(response, Response)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"message": "Successfully signed out"})


class TestGetUserView(unittest.TestCase):
    @patch("MedsRecognition.mobile_api_views.IsAuthenticated.has_permission", return_value=True)
    def test_get_user_authenticated(self, mock_permission):
        # Mock request with authenticated user
        factory = APIRequestFactory()
        request = factory.get("/")
        request.user = MagicMock()
        request.user.id = 1
        request.user.email = "testuser@example.com"
        request.user.username = "testuser"

        view = GetUserView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            {
                "id": 1,
                "email": "testuser@example.com",
                "username": "testuser",
            },
        )

    @patch("MedsRecognition.mobile_api_views.IsAuthenticated.has_permission", return_value=False)
    def test_get_user_unauthenticated(self, mock_permission):
        # Mock request with unauthenticated user
        factory = APIRequestFactory()
        request = factory.get("/")

        view = GetUserView.as_view()
        response = view(request)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# class TestMedicationsListView(unittest.TestCase):
#     def setUp(self):
#         self.factory = RequestFactory()
#         self.view = MedicationsListView.as_view()
#         self.user = MagicMock()
#         self.user.is_authenticated = True
#
#     @patch("MedsRecognition.mobile_api_views.Medication.objects.filter")
#     @patch("MedsRecognition.mobile_api_views.PageNumberPagination.paginate_queryset")
#     @patch("MedsRecognition.mobile_api_views.MedicationSerializer")
#     @patch("MedsRecognition.mobile_api_views.PageNumberPagination.get_paginated_response")
#     def test_get_medications_list_success(
#         self,
#         mock_get_paginated_response,
#         mock_serializer,
#         mock_paginate_queryset,
#         mock_filter,
#     ):
#         self.api_factory = APIRequestFactory()
#
#         mock_request = self.api_factory.get("/medications?filter=pain&sort=name")
#         mock_request.user = self.user
#
#         mock_filtered_queryset = MagicMock(spec=QuerySet)
#         mock_filter.return_value = mock_filtered_queryset
#
#         mock_paginate_queryset.return_value = mock_filtered_queryset
#
#         mock_serializer.return_value.data = [{"id": 1, "title": "Painkiller"}]
#
#         mock_paginated_response = MagicMock(spec=Response)
#         mock_paginated_response.headers = {"Vary": "Accept"}
#         mock_get_paginated_response.return_value = mock_paginated_response
#
#         response = self.view(mock_request)
#
#         mock_filter.assert_called_once_with(title__icontains="pain")
#         mock_paginate_queryset.assert_called_once()
#
#         mock_serializer.assert_called_once_with(mock_filtered_queryset, many=True)
#         mock_get_paginated_response.assert_called_once_with([{"id": 1, "title": "Painkiller"}])
#         self.assertEqual(response, mock_paginated_response)
#
#     @patch("MedsRecognition.mobile_api_views.Medication.objects.filter")
#     def test_get_medications_list_empty_filter(self, mock_filter):
#         mock_request = self.factory.get("/medications")
#         mock_request.user = self.user
#         mock_filtered_queryset = []
#         mock_filter.return_value = mock_filtered_queryset
#
#         response = self.view(mock_request)
#
#         mock_filter.assert_called_once_with(title__icontains="")
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#
#     def test_get_medications_list_unauthenticated(self):
#         mock_request = self.factory.get("/medications")
#         mock_request.user = MagicMock(is_authenticated=False)
#
#         response = self.view(mock_request)
#
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
