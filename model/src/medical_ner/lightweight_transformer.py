import logging
import os
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus

import requests
import torch
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables
MODEL_NAME = os.getenv(
    "MODEL_NAME", "d4data/biomedical-ner-all"
)  # High-accuracy biomedical NER model
DEVICE = -1 if not torch.cuda.is_available() else 0  # -1 for CPU, 0 for GPU
CACHE_SIZE = int(os.getenv("CACHE_SIZE", "1000"))  # Size of LRU cache for drug lookups
RXNORM_API_URL = os.getenv("RXNORM_API_URL", "https://rxnav.nlm.nih.gov/REST")
CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

# Types for better readability
RxConcept = Dict[str, Any]
RxNormCache = Dict[str, RxConcept]


class TextRequest(BaseModel):
    text: str = Field(..., description="Medical text to analyze")


class EntityDetail(BaseModel):
    rxcui: Optional[str] = None
    name: str
    drug_class: Optional[str] = None
    synonyms: List[str] = Field(default_factory=list)
    brand_names: List[str] = Field(default_factory=list)
    related_drugs: List[str] = Field(default_factory=list)
    strength: Optional[str] = None
    description: Optional[str] = None


class Entity(BaseModel):
    text: str
    label: str
    score: float
    details: Optional[EntityDetail] = None


class EntityResponse(BaseModel):
    entities: List[Entity] = Field(default_factory=list)


# Initialize in-memory cache
drug_cache: RxNormCache = {}


@lru_cache(maxsize=1)
def get_ner_pipeline():
    """Load the NER pipeline with caching"""
    try:
        logger.info(f"Loading NER model: {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForTokenClassification.from_pretrained(MODEL_NAME)

        # Create NER pipeline
        ner = pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
            device=DEVICE,
        )
        return ner
    except Exception as e:
        logger.error(f"Failed to load NER model: {e}")
        raise RuntimeError(f"Failed to load NER model: {e}")


class RxNormClient:
    """Client for RxNorm API to get drug information"""

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def search_by_name(drug_name: str) -> Optional[Dict]:
        """Search for drug by name in RxNorm"""
        try:
            url = f"{RXNORM_API_URL}/drugs?name={quote_plus(drug_name)}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if "drugGroup" in data and "conceptGroup" in data["drugGroup"]:
                    return data
            return None
        except Exception as e:
            logger.warning(f"Error searching RxNorm for {drug_name}: {e}")
            return None

    @staticmethod
    @lru_cache(maxsize=CACHE_SIZE)
    def get_drug_details(rxcui: str) -> Optional[Dict]:
        """Get detailed information about a drug from RxNorm"""
        try:
            url = f"{RXNORM_API_URL}/rxcui/{rxcui}/allrelated"
            response = requests.get(url)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            logger.warning(f"Error getting RxNorm details for {rxcui}: {e}")
            return None

    @staticmethod
    def extract_entity_details(drug_name: str) -> Optional[EntityDetail]:
        """Extract all relevant information for a drug from RxNorm"""
        # Normalize name (lowercase, remove non-alphanumeric)
        normalized_name = re.sub(r"[^a-zA-Z0-9]", "", drug_name.lower())

        # Check cache first
        if normalized_name in drug_cache:
            data = drug_cache[normalized_name]
            return EntityDetail(**data)

        # Search for the drug
        search_results = RxNormClient.search_by_name(drug_name)
        if not search_results:
            return None

        # Find the best match
        rxcui = None
        name = drug_name
        drug_class = None
        synonyms = []
        brand_names = []
        related_drugs = []

        # Process concept groups
        for group in search_results["drugGroup"]["conceptGroup"]:
            if "conceptProperties" in group:
                for concept in group["conceptProperties"]:
                    if concept["name"].lower() == drug_name.lower():
                        rxcui = concept["rxcui"]
                        name = concept["name"]

                        # Get detailed info if we have an RXCUI
                        if rxcui:
                            details = RxNormClient.get_drug_details(rxcui)
                            if details and "allRelatedGroup" in details:
                                # Extract information from related groups
                                for related_group in details["allRelatedGroup"][
                                    "conceptGroup"
                                ]:
                                    if "conceptProperties" in related_group:
                                        for prop in related_group["conceptProperties"]:
                                            if related_group["tty"] == "SY":  # Synonym
                                                synonyms.append(prop["name"])
                                            elif (
                                                related_group["tty"] == "BN"
                                            ):  # Brand name
                                                brand_names.append(prop["name"])
                                            elif (
                                                related_group["tty"] == "IN"
                                            ):  # Ingredient
                                                related_drugs.append(prop["name"])

        # Create entity detail
        if rxcui:
            details = EntityDetail(
                rxcui=rxcui,
                name=name,
                drug_class=drug_class,
                synonyms=list(set(synonyms)),
                brand_names=list(set(brand_names)),
                related_drugs=list(set(related_drugs)),
            )

            # Cache result
            drug_cache[normalized_name] = details.dict(exclude_none=True)
            return details

        return None


app = FastAPI(title="Advanced Medical NER Service")


@app.post("/extract_entities", response_model=EntityResponse)
def extract_entities(req: TextRequest, ner=Depends(get_ner_pipeline)) -> EntityResponse:
    """
    Extract medical entities from text using a transformer model
    and enrich with RxNorm information.
    """
    try:
        # Process text with NER pipeline
        results = ner(req.text)

        entities = []
        for result in results:
            # Skip entities with low confidence
            if result["score"] < CONFIDENCE_THRESHOLD:
                continue

            # Extract entity details
            entity_text = result["word"]
            entity_label = result["entity"]
            entity_score = result["score"]

            # Only lookup drug information for drug/chemical entities
            details = None
            if any(
                label in entity_label.lower()
                for label in ["drug", "chem", "substance", "medication"]
            ):
                details = RxNormClient.extract_entity_details(entity_text)

            # Add to results
            entities.append(
                Entity(
                    text=entity_text,
                    label=entity_label,
                    score=entity_score,
                    details=details,
                )
            )

        return EntityResponse(entities=entities)

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    try:
        # Check that model can be loaded
        get_ner_pipeline()

        # Check RxNorm API
        test_response = requests.get(f"{RXNORM_API_URL}/version")
        rx_status = "available" if test_response.status_code == 200 else "unavailable"

        return {
            "status": "ok",
            "message": "Service is healthy",
            "rxnorm_api": rx_status,
            "cached_drugs": len(drug_cache),
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")
