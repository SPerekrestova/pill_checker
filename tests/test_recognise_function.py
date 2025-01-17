from MedsRecognition.medication_views import recognise
import django
import os
import unittest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MedsRecognition.settings")

django.setup()


class TestRecogniseFunction(unittest.TestCase):
    def test_recognise_with_multiple_ingredients(self):
        extracted_text = "Sample text with IngredientA and IngredientB"
        result = recognise(extracted_text)
        self.assertEqual(result, ["IngredientA", "IngredientB"])

    def test_recognise_with_no_ingredients(self):
        extracted_text = "Sample text with no active ingredients"
        result = recognise(extracted_text)
        self.assertEqual(result, [])

    def test_recognise_removes_duplicates(self):
        extracted_text = "Sample text with IngredientA and IngredientB, and again IngredientB"
        result = recognise(extracted_text)
        self.assertEqual(result, ["IngredientA", "IngredientB"])


if __name__ == "__main__":
    unittest.main()
