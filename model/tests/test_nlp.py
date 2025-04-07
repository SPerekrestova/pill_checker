"""
Tests for the NLP service functionality.
"""

from unittest.mock import MagicMock, patch

import pytest
from medical_ner.services.nlp import get_nlp_model


def test_nlp_model_loading():
    """Test that the NLP model loads successfully"""
    # This will use the real model, so it's slow but valuable
    # You may want to skip this in CI with a decorator if it's too slow
    model = get_nlp_model()
    assert model is not None
    assert hasattr(model, "pipe_names")

    # Verify that required pipes are present
    assert "ner" in model.pipe_names
    assert "scispacy_linker" in model.pipe_names


@patch("spacy.load")
def test_nlp_model_loading_failure(mock_load):
    """Test error handling when model loading fails"""
    # Mock the spacy.load function to raise an exception
    mock_load.side_effect = OSError("Model not found")

    # The function should raise a RuntimeError with a helpful message
    with pytest.raises(RuntimeError) as excinfo:
        get_nlp_model.cache_clear()  # Clear the LRU cache
        get_nlp_model()

    assert "Error loading model" in str(excinfo.value)


@patch("spacy.load")
def test_nlp_model_caching(mock_load):
    """Test that the model is properly cached"""
    # Create a mock model
    mock_model = MagicMock()
    mock_model.pipe_names = ["ner"]
    mock_model.add_pipe.return_value = None
    mock_load.return_value = mock_model

    # Clear the cache and load the model twice
    get_nlp_model.cache_clear()
    model1 = get_nlp_model()
    model2 = get_nlp_model()

    # Verify that spacy.load was only called once
    assert mock_load.call_count == 1
    assert model1 is model2  # Same instance should be returned


def test_nlp_entity_recognition():
    """Test basic entity recognition functionality"""
    model = get_nlp_model()
    text = "The patient was prescribed ibuprofen for pain relief."
    doc = model(text)

    # Check that entities were found
    assert len(doc.ents) > 0

    # Check that at least one entity is a medication
    medications = [ent for ent in doc.ents if "ibuprofen" in ent.text.lower()]
    assert len(medications) > 0


def test_nlp_abbreviation_detection():
    """Test that abbreviation detection is working"""
    # Skip if the abbreviation detector is not available
    model = get_nlp_model()
    if "abbreviation_detector" not in model.pipe_names:
        pytest.skip("Abbreviation detector not available")

    # Test with a text containing an abbreviation
    text = "The patient has chronic obstructive pulmonary disease (COPD)."
    doc = model(text)

    # Check that abbreviations were detected
    abbreviations = []
    if hasattr(doc._, "abbreviations"):
        abbreviations = doc._.abbreviations

    assert len(abbreviations) > 0
    assert any(
        abbr._.long_form.text.lower() == "chronic obstructive pulmonary disease"
        for abbr in abbreviations
    )
