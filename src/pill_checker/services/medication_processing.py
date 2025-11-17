"""Medication processing utilities for extracting structured data from OCR text."""

import re
from typing import Any, Dict, List, Optional, Tuple


def extract_dosage(text: str) -> Optional[str]:
    """
    Extract dosage information from medication text.

    Args:
        text: OCR text from medication label

    Returns:
        Dosage string if found, None otherwise

    Examples:
        "Take 200mg daily" -> "200mg"
        "Ibuprofen 500 mg tablets" -> "500 mg"
        "0.5ml twice daily" -> "0.5ml"
    """
    # Common dosage patterns
    patterns = [
        r"(\d+(?:\.\d+)?\s*(?:mg|g|ml|mcg|µg|iu|units?))",  # 200mg, 0.5ml, 100mcg
        r"(\d+(?:\.\d+)?\s*/\s*\d+(?:\.\d+)?\s*(?:mg|ml))",  # 500/125mg
        r"(\d+(?:\.\d+)?%)",  # 5% concentration
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


def extract_title(
    text: str, entities: List[Dict[str, Any]], max_length: int = 200
) -> Optional[str]:
    """
    Extract medication title from text and entities.

    Prioritizes canonical names from NER entities, falls back to text extraction.

    Args:
        text: OCR text from medication label
        entities: List of chemical entities from NER
        max_length: Maximum length for title

    Returns:
        Medication title/name
    """
    # Try to get canonical name from first chemical entity
    if entities:
        for entity in entities:
            if entity.get("label") == "CHEMICAL":
                canonical = entity.get("canonical_name") or entity.get("text")
                if canonical:
                    # Add dosage if available
                    dosage = extract_dosage(text)
                    if dosage:
                        title = f"{canonical} {dosage}"
                    else:
                        title = canonical
                    return title[:max_length]

    # Fallback: extract first capitalized word(s) that might be a drug name
    # Look for patterns like "Ibuprofen" or "Amoxicillin"
    match = re.search(r"\b[A-Z][a-z]{2,}(?:il|in|ine|ol|one|ide)?\b", text)
    if match:
        return match.group(0)[:max_length]

    # Last resort: use first few words
    words = text.split()
    if words:
        return " ".join(words[:3])[:max_length]

    return None


def format_active_ingredients(entities: List[Dict[str, Any]]) -> str:
    """
    Format active ingredients from entity list into a string.

    Args:
        entities: List of all entities from NER

    Returns:
        Comma-separated string of unique active ingredients
    """
    chemicals = [
        entity.get("canonical_name") or entity.get("text")
        for entity in entities
        if entity.get("label") == "CHEMICAL"
    ]

    # Remove duplicates while preserving order
    seen = set()
    unique_chemicals = []
    for chem in chemicals:
        if chem and chem.lower() not in seen:
            seen.add(chem.lower())
            unique_chemicals.append(chem)

    return ", ".join(unique_chemicals) if unique_chemicals else ""


def extract_prescription_details(
    text: str, entities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract structured prescription details from text and entities.

    Args:
        text: OCR text from medication label
        entities: List of entities from NER

    Returns:
        Dictionary with prescription metadata
    """
    details: Dict[str, Any] = {}

    # Extract frequency/instructions
    frequency_patterns = [
        (r"(\d+\s*times?\s*(?:per|a|daily|day))", "frequency"),
        (r"(once|twice|three times)\s*(?:per|a)?\s*day", "frequency"),
        (r"(every\s+\d+\s+hours?)", "frequency"),
        (r"(morning|evening|bedtime|night)", "timing"),
    ]

    for pattern, key in frequency_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details[key] = match.group(1).strip()

    # Extract expiry date
    expiry_patterns = [
        r"(?:exp|expiry|expires?)[:\s]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})",
        r"(?:exp|expiry|expires?)[:\s]+(\d{2,4}[-/]\d{1,2})",
    ]

    for pattern in expiry_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            details["expiry_date"] = match.group(1).strip()
            break

    # Add disease entities if any
    diseases = [
        entity.get("canonical_name") or entity.get("text")
        for entity in entities
        if entity.get("label") == "DISEASE"
    ]
    if diseases:
        details["related_conditions"] = diseases

    # Add CUI identifiers for interoperability
    cuis = [entity.get("cui") for entity in entities if entity.get("cui")]
    if cuis:
        details["cui_identifiers"] = cuis

    return details


def process_medication_text(
    ocr_text: str, entities: List[Dict[str, Any]]
) -> Tuple[Optional[str], str, Optional[str], Dict[str, Any]]:
    """
    Process OCR text and NER entities into structured medication data.

    Args:
        ocr_text: Raw text from OCR
        entities: Entity list from BiomedNER

    Returns:
        Tuple of (title, active_ingredients, dosage, prescription_details)
    """
    title = extract_title(ocr_text, entities)
    active_ingredients = format_active_ingredients(entities)
    dosage = extract_dosage(ocr_text)
    prescription_details = extract_prescription_details(ocr_text, entities)

    return title, active_ingredients, dosage, prescription_details
