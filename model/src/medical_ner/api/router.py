from typing import Dict

from fastapi import APIRouter, Depends, HTTPException

from ..core.logging import get_logger
from ..services.linker import EntityLinker
from ..services.nlp import get_nlp_model
from .models import EntityResponse, HealthResponse, TextRequest

router = APIRouter()
logger = get_logger(__name__)


# In router.py, enhance documentation
@router.post("/extract_entities",
             response_model=EntityResponse,
             summary="Extract medical entities from text",
             description="Process the input text and return recognized medical entities along with linked knowledge base information.",
             response_description="The recognized entities with their details")
def extract_entities(req: TextRequest, nlp=Depends(get_nlp_model)) -> EntityResponse:
    """
    Process the input text and return recognized entities along with their medical details.
    """
    try:
        doc = nlp(req.text)

        # Use the entity linker service
        linker_service = EntityLinker(doc)
        entities = linker_service.extract_entities()

        return EntityResponse(entities=entities)

    except Exception as e:
        logger.error(f"Error processing text: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing text: {str(e)}")


@router.get("/health", response_model=HealthResponse)
def health_check(nlp=Depends(get_nlp_model)) -> Dict[str, str]:
    """
    Health check endpoint to verify that the application is running and the model is loaded.
    """
    try:
        # Test the model with a simple string
        nlp("test")
        return HealthResponse(
            status="ok", message="Service is healthy, model is loaded"
        )
    except Exception as e:
        raise HTTPException(
            status_code=503, detail=f"Model not properly loaded: {str(e)}"
        )
