import unittest
from unittest.mock import patch, mock_open
import json
from MedsRecognition.trade_mark_fetcher import TradeMarkFetcher


class TestTradeMarkFetcher(unittest.TestCase):

    @patch("requests.get")
    def test_fetch_trade_marks_from_openfda_success(self, mock_get):
        mock_response_data = {
            "results": [
                {"openfda": {"brand_name": ["BrandA"]}},
                {"openfda": {"brand_name": ["BrandB"]}},
            ]
        }
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = mock_response_data

        fetcher = TradeMarkFetcher()
        result = fetcher.fetch_trade_marks_from_openfda("ingredient1")
        self.assertEqual(result, ["BrandA", "BrandB"])
        mock_get.assert_called_once_with(
            "https://api.fda.gov/drug/label.json?search=active_ingredient:ingredient1&limit=100"
        )

    @patch("requests.get")
    def test_fetch_trade_marks_from_openfda_error(self, mock_get):
        mock_get.side_effect = Exception("API Error")

        fetcher = TradeMarkFetcher()
        result = fetcher.fetch_trade_marks_from_openfda("ingredient1")
        self.assertEqual(result, [])
        mock_get.assert_called_once_with(
            "https://api.fda.gov/drug/label.json?search=active_ingredient:ingredient1&limit=100"
        )

    @patch("builtins.open", new_callable=mock_open, read_data=json.dumps({}))
    @patch("os.path.exists")
    def test_load_trade_marks_from_file_exists(self, mock_exists, mock_file):
        mock_exists.return_value = True

        fetcher = TradeMarkFetcher()
        fetcher.load_trade_marks_from_file()
        self.assertEqual(fetcher.trade_marks, {})

    @patch("os.path.exists")
    def test_load_trade_marks_from_file_not_exists(self, mock_exists):
        mock_exists.return_value = False

        fetcher = TradeMarkFetcher()
        fetcher.load_trade_marks_from_file()
        self.assertEqual(fetcher.trade_marks, {})

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_fetch_trade_marks_save_to_file(self, mock_json_dump, mock_file):
        fetcher = TradeMarkFetcher()
        fetcher.fetch_trade_marks_from_openfda = patch(
            "MedsRecognition.trade_mark_fetcher.TradeMarkFetcher.fetch_trade_marks_from_openfda",
            return_value=["BrandA", "BrandB"],
        ).start()

        fetcher.fetch_trade_marks(["ingredient1", "ingredient2"])
        self.assertIn("ingredient1", fetcher.trade_marks)
        self.assertIn("ingredient2", fetcher.trade_marks)

        mock_file.assert_called_once_with("trade_marks_all.json", "w")
        mock_json_dump.assert_called_once_with(
            fetcher.trade_marks, mock_file(), indent=4
        )

    def test_find_trade_marks(self):
        fetcher = TradeMarkFetcher()
        fetcher.trade_marks = {
            "ingredient1": ["BrandA", "BrandB"],
            "ingredient2": ["BrandC"],
        }

        self.assertEqual(
            fetcher.find_trade_marks("BrandA is a medication.", ["ingredient1"]),
            "BrandA",
        )
        self.assertEqual(
            fetcher.find_trade_marks("Use BrandC for treatment.", ["ingredient2"]),
            "BrandC",
        )

        self.assertIsNone(
            fetcher.find_trade_marks("No brand mentioned here.", ["ingredient1"])
        )
        self.assertIsNone(fetcher.find_trade_marks("Different text.", ["ingredient2"]))

        fetcher.trade_marks = {}
        with self.assertRaises(ValueError):
            fetcher.find_trade_marks("Any text.", ["ingredient1"])

    @patch(
        "MedsRecognition.trade_mark_fetcher.TradeMarkFetcher.fetch_trade_marks_from_openfda",
        return_value=["BrandA"],
    )
    @patch(
        "MedsRecognition.trade_mark_fetcher.TradeMarkFetcher.load_trade_marks_from_file"
    )
    def test_get_trade_mark(self, mock_load_file, mock_fetch_trade_marks_from_openfda):
        fetcher = TradeMarkFetcher()
        fetcher.trade_marks = {"ingredient1": ["BrandA"]}

        result = fetcher.get_trade_mark("BrandA is great.", ["ingredient1"])
        self.assertEqual(result, "BrandA")

        missing_result = fetcher.get_trade_mark("No match here.", ["ingredient2"])
        self.assertIsNone(missing_result)

        mock_load_file.assert_called()
        mock_fetch_trade_marks_from_openfda.assert_called()


if __name__ == "__main__":
    unittest.main()
