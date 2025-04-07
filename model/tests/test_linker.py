"""
Tests for the entity linking service.
"""

from unittest.mock import MagicMock, patch

from medical_ner.services.linker import EntityLinker


class MockEntity:
    """Mock entity for testing"""

    def __init__(self, text, kb_ents=None):
        self.text = text
        self._ = MagicMock()
        self._.kb_ents = kb_ents or []


class MockKnowledgeBase:
    """Mock knowledge base for testing"""

    def __init__(self):
        self.cui_to_entity = {
            "C0021400": type(
                "EntityDetail",
                (),
                {
                    "canonical_name": "Ibuprofen",
                    "definition": "A non-steroidal anti-inflammatory agent with analgesic properties",
                    "aliases": ["Advil", "Motrin"],
                },
            ),
            "C0000970": type(
                "EntityDetail",
                (),
                {
                    "canonical_name": "Acetaminophen",
                    "definition": "A non-opiate analgesic with antipyretic properties",
                    "aliases": ["Paracetamol", "Tylenol"],
                },
            ),
        }


class MockLinker:
    """Mock entity linker for testing"""

    def __init__(self):
        self.kb = MockKnowledgeBase()


def test_entity_linker_initialization():
    """Test EntityLinker initialization"""
    # Create mock document
    doc = MagicMock()
    doc.ents = []

    # Add mock linker to document
    mock_linker = MockLinker()
    doc._.get_pipe.return_value = mock_linker

    # Initialize EntityLinker
    linker = EntityLinker(doc)

    assert linker.doc == doc
    assert linker.linker == mock_linker


def test_entity_linker_initialization_no_linker():
    """Test EntityLinker initialization when linker is not available"""
    # Create mock document
    doc = MagicMock()
    doc.ents = []

    # Make get_pipe raise an error
    doc._.get_pipe.side_effect = KeyError("scispacy_linker not found")

    # Initialize EntityLinker - should not raise an error
    linker = EntityLinker(doc)

    assert linker.doc == doc
    assert linker.linker is None


def test_extract_entities_empty():
    """Test extraction with no entities"""
    # Create mock document with no entities
    doc = MagicMock()
    doc.ents = []

    # Add mock linker to document
    mock_linker = MockLinker()
    doc._.get_pipe.return_value = mock_linker

    # Extract entities
    linker = EntityLinker(doc)
    entities = linker.extract_entities()

    assert len(entities) == 0


def test_extract_entities():
    """Test extraction with entities"""
    # Create mock document with entities
    doc = MagicMock()

    # Create entities with linked knowledge
    entity1 = MockEntity("ibuprofen", kb_ents=[("C0021400", 0.98)])
    entity2 = MockEntity("acetaminophen", kb_ents=[("C0000970", 0.95)])
    doc.ents = [entity1, entity2]

    # Add mock linker to document
    mock_linker = MockLinker()
    doc._.get_pipe.return_value = mock_linker

    # Extract entities
    linker = EntityLinker(doc)
    entities = linker.extract_entities()

    assert len(entities) == 2

    # Check first entity
    assert entities[0].text == "ibuprofen"
    assert len(entities[0].umls_entities) == 1
    assert entities[0].umls_entities[0].canonical_name == "Ibuprofen"
    assert "Advil" in entities[0].umls_entities[0].aliases

    # Check second entity
    assert entities[1].text == "acetaminophen"
    assert entities[1].umls_entities[0].canonical_name == "Acetaminophen"


def test_extract_entities_low_confidence():
    """Test extraction with low confidence entities that should be filtered"""
    # Create mock document with entities
    doc = MagicMock()

    # Create an entity with low confidence match
    entity = MockEntity("ibuprofen", kb_ents=[("C0021400", 0.3)])  # Low confidence
    doc.ents = [entity]

    # Add mock linker to document
    mock_linker = MockLinker()
    doc._.get_pipe.return_value = mock_linker

    # Set low threshold for testing
    with patch("medical_ner.core.config.settings.ENTITY_SCORE_THRESHOLD", 0.8):
        # Extract entities
        linker = EntityLinker(doc)
        entities = linker.extract_entities()

        # Entity should be present but with no linked entities due to low confidence
        assert len(entities) == 1
        assert entities[0].text == "ibuprofen"
        assert len(entities[0].umls_entities) == 0


def test_extract_entities_no_linker():
    """Test extraction when linker is not available"""
    # Create mock document with entities
    doc = MagicMock()
    entity = MockEntity("ibuprofen", kb_ents=[("C0021400", 0.98)])
    doc.ents = [entity]

    # Make get_pipe raise an error
    doc._.get_pipe.side_effect = KeyError("scispacy_linker not found")

    # Extract entities
    linker = EntityLinker(doc)
    entities = linker.extract_entities()

    # Entity should be present but with no linked entities
    assert len(entities) == 1
    assert entities[0].text == "ibuprofen"
    assert len(entities[0].umls_entities) == 0
