from django.test import TestCase
from unittest.mock import patch, MagicMock, mock_open

from MedsRecognition.models import UploadedImage, CustomUser, ScannedMedication
from MedsRecognition.meds_recognition import MedsRecognition


class MedsRecognitionTestCase(TestCase):
    def setUp(self):
        """Set up instances and mock dependencies for the tests."""
        # REMOVE settings.configure()
        self.meds_recognition_instance = MedsRecognition()

    def test_fetch_active_ingredients_from_file_with_uploaded_image(self):
        """Test function fetch_active_ingredients when the file exists."""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data='{"ingredients": ["Paracetamol", "Ibuprofen"]}')):
            result = self.meds_recognition_instance.fetch_active_ingredients()

        self.assertIsInstance(result, dict, "Result should be a dict.")
        self.assertIn("ingredients", result, "Dictionary must have 'ingredients' key.")
        self.assertIsInstance(result["ingredients"], list, "'ingredients' should be a list.")

    def test_uploaded_image_model_fields(self):
        """Test the UploadedImage model field behavior."""
        image = UploadedImage.objects.create(file_path="path/to/image.jpg")
        self.assertEqual(image.file_path, "path/to/image.jpg", "File path should be set.")

    def test_fetch_active_ingredients_with_empty_file_and_fallback(self):
        """Test fallback to API if the file is empty."""
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data='')), \
             patch("MedsRecognition.meds_recognition.MedsRecognition.fetch_active_ingredients_from_api",
                   return_value={"ingredients": [{"name": "Paracetamol"}]}) as mock_fetch_api:
            result = self.meds_recognition_instance.fetch_active_ingredients()
            result = [i["name"] for i in result["ingredients"]]

        mock_fetch_api.assert_called_once()
        self.assertIsInstance(result, list, "Result should be a list.")
        self.assertIn("Paracetamol", result, "'Paracetamol' should be in the result.")

    def test_fetch_active_ingredients_when_no_file_and_no_data(self):
        """Test that the function calls API when no file exists."""
        with patch("os.path.exists", return_value=False), \
                patch("MedsRecognition.meds_recognition.MedsRecognition.fetch_active_ingredients_from_api",
                      return_value={"ingredients": [{"name": "Ibuprofen"}]}) as mock_fetch_api:
            result = self.meds_recognition_instance.fetch_active_ingredients()

        mock_fetch_api.assert_called_once()
        self.assertIsInstance(result, dict, "Result should be a dict.")

        # Gather the 'name' field from each dictionary under 'ingredients'
        ingredients_list = [item["name"] for item in result["ingredients"]]
        self.assertIn("Ibuprofen", ingredients_list, "'Ibuprofen' should be in the result.")

    def test_scanned_medication_model_integration(self):
        """Test integration of ScannedMedication model with mocked API response."""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "drugMember": [
                {"minConcept": {"name": "Acetaminophen"}},
                {"minConcept": {"name": "Amoxicillin"}}
            ]
        }

        # Mock an API call with requests.get
        with patch("requests.get", return_value=mock_response):
            ScannedMedication.objects.create(
                user=CustomUser.objects.create(username="test_user"),
                prescription_details=mock_response.json.return_value
            )

        medication = ScannedMedication.objects.last()
        medication_data = medication.prescription_details
        result = [drug["minConcept"]["name"] for drug in medication_data["drugMember"]]

        self.assertIsInstance(result, list, "Result should be a list.")
        self.assertEqual(len(result), 2, "API should return exactly 2 active ingredients.")
        self.assertIn("Acetaminophen", result, "'Acetaminophen' should be in the result.")
        self.assertIn("Amoxicillin", result, "'Amoxicillin' should be in the result.")

    def test_custom_user_model_fields(self):
        """Test functionality of CustomUser model fields."""
        user = CustomUser.objects.create(username="test_user", email="test@example.com")
        self.assertEqual(user.username, "test_user", "Username should match.")
        self.assertEqual(user.email, "test@example.com", "Email should match.")

    def test_find_active_ingredients_no_match(self):
        """Test find_active_ingredients when no active ingredients are matched."""
        self.meds_recognition_instance.active_ingredients = ["Paracetamol", "Ibuprofen"]
        text = "No active ingredients in this text."
        result = self.meds_recognition_instance.find_active_ingredients(text)

        self.assertIsInstance(result, list, "Result should be a list.")
        self.assertEqual(len(result), 0, "Result should be empty as there are no matches.")

    def test_find_active_ingredients_empty_list(self):
        """Test when active_ingredients list is empty."""
        self.meds_recognition_instance.active_ingredients = []
        with self.assertRaises(ValueError, msg="Active ingredients list is not loaded."):
            self.meds_recognition_instance.find_active_ingredients("Paracetamol")

    def test_integration_of_all_models(self):
        """Test integration of all models together."""
        user = CustomUser.objects.create(username="test_user", email="test@example.com")
        UploadedImage.objects.create(file_path="path/to/image.jpg")
        medication = ScannedMedication.objects.create(
            user=user,
            prescription_details={"ingredients": ["Aspirin", "Ciprofloxacin"]}
        )

        self.assertEqual(medication.user, user, "Scanned medication should be linked to the correct user.")
        self.assertEqual(
            medication.prescription_details["ingredients"],
            ["Aspirin", "Ciprofloxacin"],
            "Medication data should match the expected ingredients."
        )

    def test_is_valid_ingredient(self):
        """Test private method _is_valid_ingredient."""
        self.assertTrue(
            self.meds_recognition_instance._is_valid_ingredient("Paracetamol"),
            "Valid ingredient should return True."
        )
        self.assertFalse(
            self.meds_recognition_instance._is_valid_ingredient(""),
            "Empty string should return False."
        )
        self.assertFalse(
            self.meds_recognition_instance._is_valid_ingredient(None),
            "None should return False."
        )
        self.assertFalse(
            self.meds_recognition_instance._is_valid_ingredient(123),
            "Non-string value should return False."
        )