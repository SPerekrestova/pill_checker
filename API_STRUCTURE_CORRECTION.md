# BiomedNER API - Actual Response Structure

## Correct API Response Format

Based on the actual pill_checker_model implementation, the `/extract_entities` endpoint returns:

```json
{
  "entities": [
    {
      "text": "ibuprofen",
      "umls_entities": [
        {
          "canonical_name": "Ibuprofen",
          "definition": "A nonsteroidal anti-inflammatory agent...",
          "aliases": ["Advil", "Motrin", "Nurofen"]
        }
      ]
    },
    {
      "text": "headache",
      "umls_entities": [
        {
          "canonical_name": "Headache",
          "definition": "Pain in the head region",
          "aliases": []
        }
      ]
    }
  ]
}
```

## Key Differences from Initial Implementation

### What the API **DOES NOT** provide:
- ❌ `label` field (CHEMICAL/DISEASE classification)
- ❌ `start`/`end` positions for entities
- ❌ `cui` field at entity level
- ❌ Flat structure with canonical_name at top level

### What the API **DOES** provide:
- ✅ `text` - the extracted entity string
- ✅ `umls_entities` - array of linked UMLS concepts (usually one)
  - ✅ `canonical_name` - standardized medical name (from RxNorm)
  - ✅ `definition` - medical description
  - ✅ `aliases` - alternative names/trade names

## Updated Implementation

### Client Method (biomed_ner_client.py)

```python
def find_active_ingredients(self, text: str) -> List[str]:
    """Extract canonical names of medical entities."""
    entities = self.extract_entities(text)
    ingredients = []

    for entity in entities:
        umls_entities = entity.get("umls_entities", [])
        if umls_entities:
            canonical_name = umls_entities[0].get("canonical_name")
            if canonical_name:
                ingredients.append(canonical_name)

    return ingredients
```

### Processing Utilities (medication_processing.py)

All helper functions updated to work with `umls_entities` structure:

```python
def format_active_ingredients(entities: List[Dict[str, Any]]) -> str:
    """Format ingredients from entities with umls_entities structure."""
    chemicals = []

    for entity in entities:
        umls_entities = entity.get("umls_entities", [])
        if umls_entities:
            canonical = umls_entities[0].get("canonical_name")
            if canonical:
                chemicals.append(canonical)

    # Deduplicate and join
    ...
```

## Test Fixtures Updated

```python
@pytest.fixture
def sample_ner_entities():
    """Sample NER entities response (actual API structure)."""
    return [
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
            "text": "pain",
            "umls_entities": [
                {
                    "canonical_name": "Pain",
                    "definition": "An unpleasant sensory experience",
                    "aliases": [],
                }
            ],
        },
    ]
```

## Files Updated

1. ✅ `src/pill_checker/services/biomed_ner_client.py` - Fixed to parse actual response
2. ✅ `src/pill_checker/services/medication_processing.py` - Work with umls_entities
3. ✅ `tests/conftest.py` - Updated fixtures to match real API
4. ✅ `tests/services/test_biomed_ner_client.py` - Tests match actual structure
5. ✅ `tests/services/test_medication_processing.py` - Tests use umls_entities
6. ✅ `tests/api/test_medication_upload.py` - Integration tests updated

## Why This Structure Makes Sense

The nested `umls_entities` structure allows for:
- **Multiple linked concepts**: One entity text can map to multiple UMLS concepts
- **Rich metadata**: Each UMLS entity contains definition and aliases
- **Flexibility**: Easy to add more linkers (MeSH, GO, HPO) without changing structure

Example with multiple matches:
```json
{
  "text": "aspirin",
  "umls_entities": [
    {
      "canonical_name": "Aspirin",
      "definition": "Acetylsalicylic acid...",
      "aliases": ["ASA", "Acetylsalicylic Acid"]
    }
    // Could have multiple UMLS matches here
  ]
}
```

## Compatibility Note

The code gracefully handles entities without UMLS data:
- Empty `umls_entities` arrays are skipped
- Missing canonical names are handled
- System falls back to text extraction if NER fails

This ensures robustness even with unexpected API responses.
