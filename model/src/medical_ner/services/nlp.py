from functools import lru_cache

import spacy
from spacy.language import Language

from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def get_nlp_model() -> Language:
    """
    Load the NLP model with caching to prevent multiple loads.
    Uses LRU cache to keep the model in memory once loaded.

    Returns:
        Language: Loaded spaCy model with all necessary components

    Raises:
        RuntimeError: If the model fails to load or a component fails to load
    """
    try:
        logger.info(f"Loading model {settings.SPACY_MODEL}...")
        model = spacy.load(settings.SPACY_MODEL)

        # Add abbreviation detector
        logger.info("Adding abbreviation detector...")
        try:
            from scispacy.abbreviation import AbbreviationDetector

            model.add_pipe("abbreviation_detector")
        except ImportError:
            logger.warning("Could not import AbbreviationDetector. Skipping.")

        # Add entity linker
        logger.info(f"Adding entity linker for {settings.LINKER_NAME}...")
        try:
            from scispacy.linking import EntityLinker

            model.add_pipe(
                "scispacy_linker",
                config={
                    "resolve_abbreviations": True,
                    "linker_name": settings.LINKER_NAME,
                },
            )
        except ImportError as e:
            logger.error(f"Failed to import EntityLinker: {e}")
            raise RuntimeError(f"Failed to import EntityLinker: {e}")
        except Exception as e:
            logger.error(f"Failed to add entity linker: {e}")
            raise RuntimeError(f"Failed to add entity linker: {e}")

        logger.info("Model successfully loaded with all components!")
        return model

    except Exception as e:
        logger.error(f"Error loading model: {e}")
        raise RuntimeError(f"Error loading model: {e}")
