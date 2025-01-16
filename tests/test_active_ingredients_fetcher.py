import unittest
from unittest.mock import patch, mock_open
import json
from MedsRecognition.active_ingredients_fetcher import ActiveIngredientsFetcher


class TestActiveIngredientsFetcher(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_active_ingredients_from_api_success(self, mock_get):
        mock_response_data = {
            "drugMemberGroup": {
                "drugMember": [
                    {"minConcept": {"name": "IngredientA"}},
                    {"minConcept": {"name": "IngredientB"}},
                ]
            }
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        result = ActiveIngredientsFetcher.fetch_active_ingredients_from_api()
        self.assertEqual(result, ["IngredientA", "IngredientB"])
        mock_get.assert_called_once_with(
            "https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?classId=0&relaSource=ATC"
        )

    @patch("requests.get")
    def test_fetch_active_ingredients_from_api_error(self, mock_get):
        mock_get.side_effect = Exception("API Error")

        with self.assertRaises(ValueError):
            ActiveIngredientsFetcher.fetch_active_ingredients_from_api()
        mock_get.assert_called_once_with(
            "https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?classId=0&relaSource=ATC"
        )

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps(["IngredientA", "IngredientB"]))
    @patch("os.path.exists")
    def test_fetch_active_ingredients_from_file_exists(self, mock_exists, mock_file):
        mock_exists.return_value = True

        fetcher = ActiveIngredientsFetcher()
        self.assertEqual(fetcher.active_ingredients, ["IngredientA", "IngredientB"])

    @patch("os.path.exists")
    def test_fetch_active_ingredients_from_file_not_exists(self, mock_exists):
        mock_exists.return_value = False

        with patch.object(ActiveIngredientsFetcher, 'fetch_active_ingredients_from_api', return_value=["IngredientA", "IngredientB"]):
            fetcher = ActiveIngredientsFetcher()
            self.assertEqual(fetcher.active_ingredients, ["IngredientA", "IngredientB"])

    def test_find_active_ingredients(self):
        fetcher = ActiveIngredientsFetcher()
        fetcher.active_ingredients = ["IngredientA", "IngredientB"]

        self.assertEqual(
            fetcher.find_active_ingredients("This contains IngredientA."),
            ["IngredientA"]
        )
        self.assertEqual(
            fetcher.find_active_ingredients("This contains IngredientB."),
            ["IngredientB"]
        )
        self.assertEqual(
            fetcher.find_active_ingredients("This contains both IngredientA and IngredientB."),
            ["IngredientA", "IngredientB"]
        )
        self.assertEqual(
            fetcher.find_active_ingredients("No ingredients here."),
            []
        )

    def test_is_valid_ingredient(self):
        self.assertTrue(ActiveIngredientsFetcher._is_valid_ingredient("IngredientA"))
        self.assertFalse(ActiveIngredientsFetcher._is_valid_ingredient(""))
        self.assertFalse(ActiveIngredientsFetcher._is_valid_ingredient(None))


if __name__ == "__main__":
    unittest.main()