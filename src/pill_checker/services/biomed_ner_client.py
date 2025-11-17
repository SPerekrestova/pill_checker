"""BiomedNER client for medical entity extraction."""

import os
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from pill_checker.core.logging_config import logger


class MedicalNERClient:
    """Client for interacting with the BiomedNER service."""

    def __init__(self, api_url: Optional[str] = None):
        """
        Initialize the MedicalNER client.

        Args:
            api_url: Optional API URL. If not provided, constructs from environment variables.
        """
        if api_url:
            self.api_url = api_url
        else:
            host = os.getenv("BIOMED_HOST")
            if not host:
                raise ValueError("Environment variable 'BIOMED_HOST' must be set.")
            scheme = os.getenv("BIOMED_SCHEME", "http")
            self.api_url = f"{scheme}://{host}"

        logger.info(f"Initialized MedicalNERClient with API URL: {self.api_url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    def extract_entities(self, text: str, timeout: int = 30) -> List[Dict[str, Any]]:
        """
        Send text to the BiomedNER API and retrieve recognized entities.

        Args:
            text: Input text to extract medical entities from
            timeout: Request timeout in seconds

        Returns:
            List of entity dictionaries with structure:
            [
                {
                    "text": "Ibuprofen",
                    "label": "CHEMICAL",
                    "start": 0,
                    "end": 9,
                    "cui": "C0020740",
                    "canonical_name": "Ibuprofen",
                    "aliases": ["Advil", "Motrin"],
                    "definition": "..."
                }
            ]

        Raises:
            RuntimeError: If the API call fails
            requests.exceptions.RequestException: If there's a network error
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to extract_entities")
            return []

        try:
            logger.debug(f"Sending text to BiomedNER API: {text[:100]}...")
            response = requests.post(
                f"{self.api_url}/extract_entities",
                json={"text": text},
                timeout=timeout,
                headers={"Content-Type": "application/json"},
            )

            if response.status_code != 200:
                error_msg = (
                    f"BiomedNER API call failed with status {response.status_code}: "
                    f"{response.text}"
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            result = response.json()
            entities = result.get("entities", [])
            logger.info(f"Extracted {len(entities)} entities from text")

            return entities

        except requests.exceptions.Timeout:
            logger.error(f"BiomedNER API request timed out after {timeout}s")
            raise RuntimeError(f"BiomedNER API request timed out after {timeout}s")
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Failed to connect to BiomedNER API: {e}")
            raise RuntimeError(f"Failed to connect to BiomedNER API at {self.api_url}")
        except Exception as e:
            logger.error(f"Unexpected error in extract_entities: {e}")
            raise

    def find_active_ingredients(self, text: str) -> List[str]:
        """
        Extract only the text of chemical/drug entities (backward compatibility).

        Args:
            text: Input text to extract active ingredients from

        Returns:
            List of active ingredient names (strings only)
        """
        entities = self.extract_entities(text)
        # Filter for CHEMICAL entities and return just the text
        ingredients = [
            entity["text"] for entity in entities if entity.get("label") == "CHEMICAL"
        ]
        return ingredients

    def find_chemicals(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract full chemical/drug entity information.

        Args:
            text: Input text to extract chemicals from

        Returns:
            List of chemical entity dictionaries with full metadata
        """
        entities = self.extract_entities(text)
        return [entity for entity in entities if entity.get("label") == "CHEMICAL"]

    def find_diseases(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract disease entity information.

        Args:
            text: Input text to extract diseases from

        Returns:
            List of disease entity dictionaries with full metadata
        """
        entities = self.extract_entities(text)
        return [entity for entity in entities if entity.get("label") == "DISEASE"]


# Singleton instance
_ner_client: Optional[MedicalNERClient] = None


def get_ner_client(api_url: Optional[str] = None) -> MedicalNERClient:
    """
    Get or create the MedicalNER client singleton.

    Args:
        api_url: Optional API URL override

    Returns:
        MedicalNERClient instance
    """
    global _ner_client
    if _ner_client is None or api_url:
        _ner_client = MedicalNERClient(api_url=api_url)
    return _ner_client
