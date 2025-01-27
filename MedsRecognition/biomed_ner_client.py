import requests


class MedicalNERClient:
    def __init__(self, api_url="http://localhost:8000"):
        self.api_url = api_url

    def find_active_ingredients(self, text):
        """
        Sends text to the API and retrieves recognized entities.
        """
        response = requests.post(f"{self.api_url}/extract_entities", json={"text": text})
        if response.status_code != 200:
            raise RuntimeError(
                f"API call failed with status {response.status_code}: {response.text}"
            )
        return response.json()
