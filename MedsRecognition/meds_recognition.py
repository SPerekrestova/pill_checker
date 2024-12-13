import pandas as pd
import re

class MedsRecognition:
    DEFAULT_FILEPATH = 'MedsRecognition/resources/medicines.csv'

    def __init__(self, filepath=None):
        self.filepath = filepath or self.DEFAULT_FILEPATH
        self.meds_df = self.load_data()

    def load_data(self):
        try:
            meds_df = pd.read_csv(self.filepath, sep=';')
            # Validate that the column exists
            if 'ActiveSubstance' not in meds_df.columns:
                raise KeyError("The required column 'ActiveSubstance' is missing.")

            # Convert all values in 'ActiveSubstance' to strings and handle NaN
            meds_df['ActiveSubstance'] = meds_df['ActiveSubstance'].fillna('').astype(str)
            return meds_df
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: File '{self.filepath}' not found.")
        except pd.errors.ParserError:
            raise ValueError("Error: Malformed CSV file.")

    def search_by_name(self, name):
        if self.meds_df is None:
            raise ValueError("Data not loaded. Ensure the file exists.")
        return self.meds_df[self.meds_df.NameOfMedicine == name].to_markdown()

    def search_by_ingredient(self, ingredient):
        if self.meds_df is None:
            raise ValueError("Data not loaded. Ensure the file exists.")
        return self.meds_df[self.meds_df.ActiveSubstance == ingredient].to_markdown()

    def find_active_ingredients(self, text):
        if self.meds_df is None or 'ActiveSubstance' not in self.meds_df.columns:
            raise ValueError("Active ingredients database is not loaded or incomplete.")

        active_ingredients = []
        for ingredient in self.meds_df['ActiveSubstance']:
            # Skip non-string or empty values
            if not isinstance(ingredient, str) or not ingredient.strip():
                continue
            # Check if the ingredient is in the text
            if re.search(rf'\b{re.escape(ingredient)}\b', text, re.IGNORECASE):
                active_ingredients.append(ingredient)
        return active_ingredients