"""Tests for the BiomedNER client."""

import pytest
from unittest.mock import Mock, patch
import requests

from pill_checker.services.biomed_ner_client import MedicalNERClient, get_ner_client


class TestMedicalNERClient:
    """Test suite for MedicalNERClient."""

    @pytest.fixture
    def mock_api_url(self):
        """Provide a mock API URL for testing."""
        return "http://localhost:8001"

    @pytest.fixture
    def ner_client(self, mock_api_url):
        """Create a NER client instance for testing."""
        return MedicalNERClient(api_url=mock_api_url)

    @pytest.fixture
    def sample_entities_response(self):
        """Sample response from BiomedNER API (actual structure)."""
        return {
            "entities": [
                {
                    "text": "ibuprofen",
                    "umls_entities": [
                        {
                            "canonical_name": "Ibuprofen",
                            "definition": "A nonsteroidal anti-inflammatory drug",
                            "aliases": ["Advil", "Motrin", "Nurofen"],
                        }
                    ],
                },
                {
                    "text": "headache",
                    "umls_entities": [
                        {
                            "canonical_name": "Headache",
                            "definition": "Pain in the head region",
                            "aliases": [],
                        }
                    ],
                },
            ]
        }

    def test_init_with_api_url(self, mock_api_url):
        """Test initialization with explicit API URL."""
        client = MedicalNERClient(api_url=mock_api_url)
        assert client.api_url == mock_api_url

    def test_init_with_env_vars(self, monkeypatch):
        """Test initialization with environment variables."""
        monkeypatch.setenv("BIOMED_HOST", "biomedner.example.com")
        monkeypatch.setenv("BIOMED_SCHEME", "https")

        client = MedicalNERClient()
        assert client.api_url == "https://biomedner.example.com"

    def test_init_missing_env_var(self, monkeypatch):
        """Test that initialization fails without BIOMED_HOST."""
        monkeypatch.delenv("BIOMED_HOST", raising=False)

        with pytest.raises(ValueError, match="BIOMED_HOST"):
            MedicalNERClient()

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_extract_entities_success(
        self, mock_post, ner_client, sample_entities_response
    ):
        """Test successful entity extraction."""
        # Mock successful API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_entities_response
        mock_post.return_value = mock_response

        # Call extract_entities
        text = "Ibuprofen 200mg for headache"
        entities = ner_client.extract_entities(text)

        # Verify API was called correctly
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:8001/extract_entities"
        assert call_args[1]["json"] == {"text": text}
        assert call_args[1]["timeout"] == 30

        # Verify entities returned
        assert len(entities) == 2
        assert entities[0]["text"] == "ibuprofen"
        assert "umls_entities" in entities[0]
        assert entities[0]["umls_entities"][0]["canonical_name"] == "Ibuprofen"

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_extract_entities_empty_text(self, mock_post, ner_client):
        """Test that empty text returns empty list."""
        result = ner_client.extract_entities("")
        assert result == []
        mock_post.assert_not_called()

        result = ner_client.extract_entities("   ")
        assert result == []
        mock_post.assert_not_called()

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_extract_entities_api_error(self, mock_post, ner_client):
        """Test handling of API errors."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        with pytest.raises(RuntimeError, match="API call failed with status 500"):
            ner_client.extract_entities("Test text")

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_extract_entities_timeout(self, mock_post, ner_client):
        """Test handling of timeout errors."""
        mock_post.side_effect = requests.exceptions.Timeout()

        with pytest.raises(RuntimeError, match="timed out"):
            ner_client.extract_entities("Test text")

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_extract_entities_connection_error(self, mock_post, ner_client):
        """Test handling of connection errors."""
        mock_post.side_effect = requests.exceptions.ConnectionError()

        with pytest.raises(RuntimeError, match="Failed to connect"):
            ner_client.extract_entities("Test text")

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_extract_entities_retry(self, mock_post, ner_client):
        """Test retry logic on transient failures."""
        # First two calls fail, third succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 503
        mock_response_fail.text = "Service Unavailable"

        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {"entities": []}

        mock_post.side_effect = [
            mock_response_fail,
            mock_response_fail,
            mock_response_success,
        ]

        # Should succeed after retries
        entities = ner_client.extract_entities("Test text")
        assert entities == []
        assert mock_post.call_count == 3

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_find_active_ingredients(self, mock_post, ner_client, sample_entities_response):
        """Test extracting active ingredient names."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_entities_response
        mock_post.return_value = mock_response

        ingredients = ner_client.find_active_ingredients("Ibuprofen 200mg for headache")

        assert len(ingredients) == 2
        assert "Ibuprofen" in ingredients
        assert "Headache" in ingredients

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_get_entity_details(self, mock_post, ner_client, sample_entities_response):
        """Test extracting full entity details."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = sample_entities_response
        mock_post.return_value = mock_response

        entities = ner_client.get_entity_details("Ibuprofen 200mg for headache")

        assert len(entities) == 2
        assert entities[0]["text"] == "ibuprofen"
        assert entities[0]["umls_entities"][0]["canonical_name"] == "Ibuprofen"
        assert "Advil" in entities[0]["umls_entities"][0]["aliases"]

    def test_get_ner_client_singleton(self, mock_api_url):
        """Test that get_ner_client returns singleton."""
        # Reset global client
        import pill_checker.services.biomed_ner_client as ner_module

        ner_module._ner_client = None

        client1 = get_ner_client(api_url=mock_api_url)
        client2 = get_ner_client()

        assert client1 is client2
        assert client1.api_url == mock_api_url

    @patch("pill_checker.services.biomed_ner_client.requests.post")
    def test_custom_timeout(self, mock_post, ner_client):
        """Test custom timeout parameter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"entities": []}
        mock_post.return_value = mock_response

        ner_client.extract_entities("Test text", timeout=60)

        call_args = mock_post.call_args
        assert call_args[1]["timeout"] == 60
