import pytest
from fastapi.testclient import TestClient
from medical_ner.main import app
from medical_ner.services.nlp import get_nlp_model


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


@pytest.fixture
def client():
    """Create a test client with mocked NLP model"""
    app.dependency_overrides[get_nlp_model] = lambda: DummyNLP()
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()
