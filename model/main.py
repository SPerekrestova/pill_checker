import logging
import os
from contextlib import asynccontextmanager
from functools import lru_cache
from typing import Dict, List, Optional

import spacy
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Environment variables with defaults
MODEL_NAME = os.getenv("SPACY_MODEL", "en_ner_bc5cdr_md")
LINKER_NAME = os.getenv("LINKER_NAME", "rxnorm")


class TextRequest(BaseModel):
    text: str = Field(..., description="Medical text to analyze")


class EntityDetail(BaseModel):
    canonical_name: str
    definition: Optional[str] = None
    aliases: List[str] = Field(default_factory=list)


class Entity(BaseModel):
    text: str
    umls_entities: List[EntityDetail] = Field(default_factory=list)


class EntityResponse(BaseModel):
    entities: List[Entity] = Field(default_factory=list)


@lru_cache(maxsize=1)
def get_nlp_model():
    """
    Load the NLP model with caching to prevent multiple loads.
    Uses LRU cache to keep the model in memory once loaded.
    """
    try:
        logger.info(f"Loading model {MODEL_NAME}...")
        model = spacy.load(MODEL_NAME)

        # Add abbreviation detector
        logger.info("Adding abbreviation detector...")
        try:
            from scispacy.abbreviation import AbbreviationDetector  # noqa: F401

            model.add_pipe("abbreviation_detector")
        except ImportError:
            logger.warning("Could not import AbbreviationDetector. Skipping.")

        # Add entity linker
        logger.info(f"Adding entity linker for {LINKER_NAME}...")
        try:
            from scispacy.linking import EntityLinker  # noqa: F401

            model.add_pipe(
                "scispacy_linker",
                config={"resolve_abbreviations": True, "linker_name": LINKER_NAME},
            )
        except ImportError as e:
            logger.error(f"Failed to import EntityLinker: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to add entity linker: {e}")
            raise

        logger.info("Model successfully loaded with all components!")
        return model

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Preload the model at startup
    try:
        get_nlp_model()
        logger.info("Model preloaded successfully")
    except Exception as e:
        logger.error(f"Failed to preload model: {e}")
    yield


app = FastAPI(
    lifespan=lifespan,
    title="Medical NER Service",
    description="A service for medical named entity recognition and linking",
)


@app.post("/extract_entities", response_model=EntityResponse)
def extract_entities(req: TextRequest, nlp=Depends(get_nlp_model)) -> EntityResponse:
    """
    Process the input text and return recognized entities along with their medical details.
    """
    try:
        doc = nlp(req.text)
        entities = []

        # Get the linker component
        try:
            linker = nlp.get_pipe("scispacy_linker")
        except KeyError:
            logger.error("scispacy_linker not found in pipeline")
            raise HTTPException(status_code=500, detail="Entity linker not available")

        # Process entities
        for ent in doc.ents:
            umls_entities = []

            # Get linked entities if available
            if hasattr(ent._, "kb_ents") and ent._.kb_ents:
                for umls_ent in ent._.kb_ents:
                    entity_id = umls_ent[0]
                    entity_detail = linker.kb.cui_to_entity.get(entity_id)

                    if entity_detail:
                        umls_entities.append(
                            EntityDetail(
                                canonical_name=entity_detail.canonical_name,
                                definition=getattr(entity_detail, "definition", None),
                                aliases=getattr(entity_detail, "aliases", []),
                            )
                        )

            # Add entity even if no UMLS links found
            entities.append(Entity(text=ent.text, umls_entities=umls_entities))

        return EntityResponse(entities=entities)

    except Exception as e:
        logger.error(f"Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@app.get("/health")
def health_check(nlp=Depends(get_nlp_model)) -> Dict[str, str]:
    """
    Health check endpoint to verify that the application is running and the model is loaded.
    """
    try:
        # Test the model with a simple string
        nlp("test")
        return {"status": "ok", "message": "Service is healthy, model is loaded"}
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Model not properly loaded: {str(e)}")
