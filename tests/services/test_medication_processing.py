"""Tests for medication processing utilities."""

import pytest
from pill_checker.services.medication_processing import (
    extract_dosage,
    extract_title,
    format_active_ingredients,
    extract_prescription_details,
    process_medication_text,
)


class TestExtractDosage:
    """Tests for dosage extraction."""

    @pytest.mark.parametrize(
        "text,expected",
        [
            ("Take 200mg daily", "200mg"),
            ("Ibuprofen 500 mg tablets", "500 mg"),
            ("0.5ml twice daily", "0.5ml"),
            ("Apply 100mcg patch", "100mcg"),
            ("Inject 10iu daily", "10iu"),
            ("500/125mg combination", "500/125mg"),
            ("Apply 5% cream", "5%"),
            ("PARACETAMOL 500MG TABLETS", "500MG"),  # Case insensitive
        ],
    )
    def test_extract_dosage_success(self, text, expected):
        """Test successful dosage extraction from various formats."""
        result = extract_dosage(text)
        assert result == expected

    def test_extract_dosage_not_found(self):
        """Test when no dosage is present."""
        result = extract_dosage("Take this medication as prescribed")
        assert result is None

    def test_extract_dosage_empty(self):
        """Test with empty string."""
        result = extract_dosage("")
        assert result is None


class TestExtractTitle:
    """Tests for medication title extraction."""

    def test_extract_title_from_entity(self):
        """Test extracting title from NER entity."""
        text = "Ibuprofen 200mg tablets take twice daily"
        entities = [
            {
                "text": "ibuprofen",
                "umls_entities": [
                    {
                        "canonical_name": "Ibuprofen",
                        "definition": "...",
                        "aliases": [],
                    }
                ],
            }
        ]

        result = extract_title(text, entities)
        assert result == "Ibuprofen 200mg"

    def test_extract_title_canonical_name(self):
        """Test that canonical name is preferred over text."""
        text = "Advil 200mg"
        entities = [
            {
                "text": "advil",
                "umls_entities": [
                    {
                        "canonical_name": "Ibuprofen",
                        "definition": "...",
                        "aliases": ["Advil"],
                    }
                ],
            }
        ]

        result = extract_title(text, entities)
        assert result == "Ibuprofen 200mg"

    def test_extract_title_no_dosage(self):
        """Test title extraction without dosage."""
        text = "Paracetamol tablets"
        entities = [
            {
                "text": "paracetamol",
                "umls_entities": [
                    {
                        "canonical_name": "Acetaminophen",
                        "definition": "...",
                        "aliases": [],
                    }
                ],
            }
        ]

        result = extract_title(text, entities)
        assert result == "Acetaminophen"

    def test_extract_title_fallback_pattern(self):
        """Test fallback to text pattern when no entities."""
        text = "Amoxicillin capsules for infection"
        entities = []

        result = extract_title(text, entities)
        assert result == "Amoxicillin"

    def test_extract_title_fallback_first_words(self):
        """Test fallback to first words."""
        text = "some medication label text"
        entities = []

        result = extract_title(text, entities)
        assert result == "some medication label"

    def test_extract_title_max_length(self):
        """Test that title respects max length."""
        text = "A" * 300
        entities = [
            {
                "text": "A" * 300,
                "label": "CHEMICAL",
                "canonical_name": "A" * 300,
            }
        ]

        result = extract_title(text, entities, max_length=50)
        assert len(result) <= 50

    def test_extract_title_empty_umls(self):
        """Test fallback when entity has no umls_entities."""
        text = "Headache medication"
        entities = [
            {"text": "Headache", "umls_entities": []},
        ]

        result = extract_title(text, entities)
        # Should fallback since no UMLS entities with canonical names
        assert result is not None


class TestFormatActiveIngredients:
    """Tests for active ingredients formatting."""

    def test_format_single_ingredient(self):
        """Test formatting single active ingredient."""
        entities = [
            {
                "text": "ibuprofen",
                "umls_entities": [{"canonical_name": "Ibuprofen", "definition": "...", "aliases": []}],
            }
        ]

        result = format_active_ingredients(entities)
        assert result == "Ibuprofen"

    def test_format_multiple_ingredients(self):
        """Test formatting multiple active ingredients."""
        entities = [
            {
                "text": "amoxicillin",
                "umls_entities": [
                    {"canonical_name": "Amoxicillin", "definition": "...", "aliases": []}
                ],
            },
            {
                "text": "clavulanic acid",
                "umls_entities": [
                    {"canonical_name": "Clavulanic Acid", "definition": "...", "aliases": []}
                ],
            },
        ]

        result = format_active_ingredients(entities)
        assert result == "Amoxicillin, Clavulanic Acid"

    def test_format_removes_duplicates(self):
        """Test that duplicate ingredients are removed."""
        entities = [
            {
                "text": "ibuprofen",
                "umls_entities": [{"canonical_name": "Ibuprofen", "definition": "...", "aliases": []}],
            },
            {
                "text": "ibuprofen",
                "umls_entities": [{"canonical_name": "Ibuprofen", "definition": "...", "aliases": []}],
            },
        ]

        result = format_active_ingredients(entities)
        assert result == "Ibuprofen"

    def test_format_ignores_empty_umls(self):
        """Test that entities without UMLS data are ignored."""
        entities = [
            {
                "text": "ibuprofen",
                "umls_entities": [{"canonical_name": "Ibuprofen", "definition": "...", "aliases": []}],
            },
            {"text": "headache", "umls_entities": []},
        ]

        result = format_active_ingredients(entities)
        assert result == "Ibuprofen"

    def test_format_empty_entities(self):
        """Test with empty entity list."""
        result = format_active_ingredients([])
        assert result == ""

    def test_format_empty_umls_entities(self):
        """Test handling entities with empty umls_entities."""
        entities = [
            {"text": "aspirin", "umls_entities": []},
        ]

        result = format_active_ingredients(entities)
        assert result == ""


class TestExtractPrescriptionDetails:
    """Tests for prescription details extraction."""

    def test_extract_frequency(self):
        """Test extracting dosage frequency."""
        text = "Take 2 tablets twice a day"
        entities = []

        details = extract_prescription_details(text, entities)
        assert "frequency" in details
        assert "twice" in details["frequency"].lower()

    def test_extract_various_frequencies(self):
        """Test various frequency patterns."""
        test_cases = [
            ("once per day", "frequency"),
            ("three times daily", "frequency"),
            ("every 4 hours", "frequency"),
            ("2 times a day", "frequency"),
        ]

        for text, expected_key in test_cases:
            details = extract_prescription_details(text, entities=[])
            assert expected_key in details

    def test_extract_timing(self):
        """Test extracting timing information."""
        text = "Take in the morning with food"
        entities = []

        details = extract_prescription_details(text, entities)
        assert "timing" in details
        assert "morning" in details["timing"].lower()

    def test_extract_expiry_date(self):
        """Test extracting expiry dates."""
        test_cases = [
            "Exp: 12/2025",
            "Expiry: 01-2026",
            "Expires 06/24",
            "EXP 2025-12",
        ]

        for text in test_cases:
            details = extract_prescription_details(text, entities=[])
            assert "expiry_date" in details

    def test_extract_detected_entities(self):
        """Test extracting detected entities."""
        text = "For pain and fever"
        entities = [
            {
                "text": "pain",
                "umls_entities": [{"canonical_name": "Pain", "definition": "...", "aliases": []}],
            },
            {
                "text": "fever",
                "umls_entities": [{"canonical_name": "Fever", "definition": "...", "aliases": []}],
            },
        ]

        details = extract_prescription_details(text, entities)
        assert "detected_entities" in details
        assert "Pain" in details["detected_entities"]
        assert "Fever" in details["detected_entities"]

    def test_extract_empty_text(self):
        """Test with minimal information."""
        details = extract_prescription_details("", [])
        assert isinstance(details, dict)


class TestProcessMedicationText:
    """Tests for the complete medication text processing."""

    def test_process_complete_medication(self):
        """Test processing complete medication information."""
        ocr_text = "Ibuprofen 200mg tablets. Take 2 tablets twice daily for pain. Exp: 12/2025"
        entities = [
            {
                "text": "ibuprofen",
                "umls_entities": [
                    {"canonical_name": "Ibuprofen", "definition": "...", "aliases": []}
                ],
            },
            {
                "text": "pain",
                "umls_entities": [{"canonical_name": "Pain", "definition": "...", "aliases": []}],
            },
        ]

        title, ingredients, dosage, details = process_medication_text(ocr_text, entities)

        assert "Ibuprofen" in title
        assert "200mg" in title
        assert "Ibuprofen" in ingredients
        assert "Pain" in ingredients
        assert dosage == "200mg"
        assert "frequency" in details
        assert "expiry_date" in details
        assert "detected_entities" in details

    def test_process_minimal_medication(self):
        """Test processing with minimal information."""
        ocr_text = "Some medication"
        entities = []

        title, ingredients, dosage, details = process_medication_text(ocr_text, entities)

        assert title is not None  # Should have fallback
        assert ingredients == ""  # No chemicals found
        assert dosage is None  # No dosage found
        assert isinstance(details, dict)

    def test_process_multiple_ingredients(self):
        """Test processing medication with multiple active ingredients."""
        ocr_text = "Amoxicillin 500mg and Clavulanic Acid 125mg tablets"
        entities = [
            {
                "text": "amoxicillin",
                "umls_entities": [
                    {"canonical_name": "Amoxicillin", "definition": "...", "aliases": []}
                ],
            },
            {
                "text": "clavulanic acid",
                "umls_entities": [
                    {"canonical_name": "Clavulanic Acid", "definition": "...", "aliases": []}
                ],
            },
        ]

        title, ingredients, dosage, details = process_medication_text(ocr_text, entities)

        assert "Amoxicillin" in title
        assert "Amoxicillin" in ingredients
        assert "Clavulanic Acid" in ingredients
        assert dosage == "500mg"  # First dosage found
