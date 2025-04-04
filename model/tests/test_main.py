from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from main import app, get_nlp_model


# Fixture to provide a test client
@pytest.fixture
def client():
    app.dependency_overrides[get_nlp_model] = lambda: DummyNLP()
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


# Dummy NLP model for testing
class DummyNLP:
    def __call__(self, text):
        return DummyDoc(text)

    @staticmethod
    def get_pipe(name):
        if name == "scispacy_linker":
            return DummyLinker()
        raise KeyError(f"Pipeline component {name} not found")


class DummyDoc:
    def __init__(self, text):
        self.ents = [DummyEntity(text)]


class DummyEntity:
    def __init__(self, text):
        self.text = text
        self._ = DummyEntityAttributes()


class DummyEntityAttributes:
    @property
    def kb_ents(self):
        return [("C0000001", 0.95)]


class DummyLinker:
    @property
    def kb(self):
        return DummyKB()


class DummyKB:
    @property
    def cui_to_entity(self):
        return {"C0000001": DummyEntityDetail()}


class DummyEntityDetail:
    @property
    def canonical_name(self):
        return "Test Entity"

    @property
    def definition(self):
        return "A test entity for unit testing."

    @property
    def aliases(self):
        return ["Test Alias 1", "Test Alias 2"]


# Test to ensure the model loads correctly
def test_model_loading(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "Service is healthy, model is loaded"}


# Test entity extraction with mock data
def test_extract_entities(client):
    response = client.post("/extract_entities", json={"text": "Test text"})
    assert response.status_code == 200
    data = response.json()
    assert "entities" in data
    assert len(data["entities"]) > 0
    entity = data["entities"][0]
    assert entity["text"] == "Test text"
    assert len(entity["umls_entities"]) > 0
    umls_entity = entity["umls_entities"][0]
    assert umls_entity["canonical_name"] == "Test Entity"
    assert umls_entity["definition"] == "A test entity for unit testing."
    assert "Test Alias 1" in umls_entity["aliases"]


# Test error handling during entity extraction
def test_extract_entities_error_handling(client):
    with patch("main.get_nlp_model", side_effect=Exception("Test exception")):
        response = client.post("/extract_entities", json={"text": "Test text"})
        assert response.status_code == 500
        assert "Error processing text: Test exception" in response.json()["detail"]


# Test health check endpoint error handling
def test_health_check_error_handling(client):
    with patch("main.get_nlp_model", side_effect=Exception("Test exception")):
        response = client.get("/health")
        assert response.status_code == 503
        assert "Model not properly loaded: Test exception" in response.json()["detail"]
