import re
import requests
import json
import os


class ActiveIngredientsFetcher:
    def __init__(self):
        self.active_ingredients = ActiveIngredientsFetcher.fetch_active_ingredients()

    @staticmethod
    def fetch_active_ingredients():
        if os.path.exists("active_ingredients.json"):
            with open("active_ingredients.json", "r") as file:
                try:
                    data = json.load(file) or {}
                except (json.JSONDecodeError, ValueError):
                    return ActiveIngredientsFetcher.fetch_active_ingredients_from_api()
                if data:
                    return data

        # If file doesn't exist or JSON is empty/invalid, fetch from API
        return ActiveIngredientsFetcher.fetch_active_ingredients_from_api()

    @staticmethod
    def fetch_active_ingredients_from_api():
        try:
            url = (
                "https://rxnav.nlm.nih.gov/REST/rxclass/classMembers.json?classId=0&relaSource=ATC"
            )
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            ingredients = [
                item["minConcept"]["name"]
                for item in data.get("drugMemberGroup", {}).get("drugMember", [])
                if "minConcept" in item and "name" in item["minConcept"]
            ]
            with open("active_ingredients.json", "w") as file:
                json.dump(ingredients, file, indent=4)
            return ingredients
        except Exception as e:
            raise ValueError(f"Error while fetching active ingredients from API: {e}")

    def find_active_ingredients(self, text):
        if not self.active_ingredients:
            raise ValueError("ActiveIngredientsFetcher ingredients list is not loaded.")
        active_ingredients = [
            ingredient
            for ingredient in self.active_ingredients
            if self._is_valid_ingredient(ingredient)
            and re.search(rf"\b{re.escape(ingredient)}\b", text, re.IGNORECASE)
        ]
        return active_ingredients

    @staticmethod
    def _is_valid_ingredient(ingredient):
        return isinstance(ingredient, str) and ingredient.strip()
