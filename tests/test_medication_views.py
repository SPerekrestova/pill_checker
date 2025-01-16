import os
import uuid
import io
from unittest import TestCase
from unittest.mock import patch, MagicMock

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MedsRecognition.settings")
import django
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.template.response import TemplateResponse
from django.test import RequestFactory

from MedsRecognition.medication_views import upload_image


class UploadImageViewUnitTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

    @patch("MedsRecognition.medication_views.ScannedMedication.objects.create")
    @patch("MedsRecognition.medication_views.TradeMarkFetcher.get_trade_mark")
    @patch("MedsRecognition.medication_views.recognise")
    @patch("MedsRecognition.medication_views.extract_text_with_easyocr")
    @patch("MedsRecognition.medication_views.Image.open")
    @patch("MedsRecognition.medication_views.ImageUploadForm")
    def test_upload_image_success(
        self,
        mock_form_class,
        mock_image_open,
        mock_extract_text,
        mock_recognise,
        mock_get_trade_mark,
        mock_scanned_create,
    ):
        dummy_image = MagicMock()
        dummy_image.mode = "RGB"
        mock_image_open.return_value = dummy_image

        mock_extract_text.return_value = "extracted text"
        mock_recognise.return_value = ["ingredient1", "ingredient2"]
        mock_get_trade_mark.return_value = "BrandA"

        dummy_profile = MagicMock()
        dummy_profile.user_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        dummy_profile.id = 123

        uploaded_file = SimpleUploadedFile(
            "test_image.jpg", b"fake image data", content_type="image/jpeg"
        )
        post_data = {"image": uploaded_file}
        request = self.factory.post("/upload_image/", post_data)
        request.session = {"supabase_user": dummy_profile.user_id}
        request.auth_user = dummy_profile

        mock_form_instance = MagicMock()
        mock_form_instance.is_valid.return_value = True
        mock_form_instance.cleaned_data = {"image": uploaded_file}
        mock_form_class.return_value = mock_form_instance

        response = upload_image(request)

        mock_scanned_create.assert_called_once_with(
            profile=dummy_profile,
            active_ingredients="ingredient1, ingredient2",
            scanned_text="extracted text",
            medication_name="BrandA",
        )

        self.assertIsInstance(response, TemplateResponse)
        self.assertEqual(response.template_name, "recognition/result.html")
        context = response.context_data
        self.assertEqual(context.get("text"), "extracted text")
        self.assertEqual(context.get("active_ingredients"), ["ingredient1", "ingredient2"])
        self.assertEqual(context.get("trade_marks"), "BrandA")