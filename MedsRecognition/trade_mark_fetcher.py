import requests
import json
import re
import os


class TradeMarkFetcher:
    def __init__(self):
        self.trade_marks = {}

    def fetch_trade_marks_from_openfda(self, active_ingredient):
        """Fetch trademarks from openFDA API (US database) for a single active ingredient."""
        try:
            url = f"https://api.fda.gov/drug/label.json?search=active_ingredient:{active_ingredient}&limit=100"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return [
                item["openfda"]["brand_name"][0]
                for item in data.get("results", [])
                if "openfda" in item and "brand_name" in item["openfda"]
            ]
        except Exception as e:
            print(f"Error fetching data for '{active_ingredient}' from openFDA: {e}")
            return []

    def fetch_trade_marks(self, active_ingredients):
        """Fetch trade marks for multiple active ingredients and store them in a JSON file."""
        try:
            for active_ingredient in active_ingredients:
                # Skip fetching if trademarks are already loaded
                if active_ingredient in self.trade_marks:
                    print(
                        f"Trademarks for '{active_ingredient}' already loaded. Skipping fetch."
                    )
                    continue

                print(
                    f"Fetching trade marks for active ingredient: {active_ingredient}"
                )
                trade_marks = self.fetch_trade_marks_from_openfda(active_ingredient)
                print(f"Trade marks fetched for '{active_ingredient}': {trade_marks}")

                # Store results in a dictionary
                self.trade_marks[active_ingredient] = list(set(trade_marks))

            # Save results to a JSON file
            filename = "trade_marks_all.json"
            with open(filename, "w") as file:
                json.dump(self.trade_marks, file, indent=4)

            print(f"Combined trade marks saved to {filename}")
        except Exception as e:
            raise ValueError(f"Error while fetching trade marks: {e}")

    def load_trade_marks_from_file(self):
        """Load trade marks from a JSON file if it exists."""
        filename = "trade_marks_all.json"
        if os.path.exists(filename):
            with open(filename, "r") as file:
                self.trade_marks = json.load(file)
            print(f"Trade marks loaded from {filename}")
        else:
            print("No trade marks file found. Starting fresh.")

    def find_trade_marks(self, text, active_ingredients):
        """
        Find the first trade mark in the given text based on a list of active ingredients.

        Args:
            text (str): The text to search for trade marks.
            active_ingredients (list): A list of active ingredients to filter trade marks.

        Returns:
            str: The first trade mark found in the text or None if no match is found.
        """
        if not self.trade_marks:
            raise ValueError("Trade marks list is not loaded.")

        for ingredient in active_ingredients:
            if ingredient in self.trade_marks:
                for trade_mark in self.trade_marks[ingredient]:
                    if re.search(rf"\b{re.escape(trade_mark)}\b", text, re.IGNORECASE):
                        return trade_mark  # Return the first trade mark found
        return None  # No trade marks found

    def get_trade_mark(self, text, active_ingredients):
        """
        High-level method to fetch trademarks if necessary, load them, and find one in the text.

        Args:
            text (str): The text to search for trade marks.
            active_ingredients (list): A list of active ingredients.

        Returns:
            str: The first trade mark found in the text or None if no match is found.
        """
        # Load trade marks from file if available
        self.load_trade_marks_from_file()

        # Fetch trade marks for any missing active ingredients
        missing_ingredients = [
            ingredient
            for ingredient in active_ingredients
            if ingredient not in self.trade_marks
        ]
        if missing_ingredients:
            self.fetch_trade_marks(missing_ingredients)

        # Find and return the first trade mark in the text
        return self.find_trade_marks(text, active_ingredients)
