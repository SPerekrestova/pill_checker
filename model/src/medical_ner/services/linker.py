"""
Entity linking service for medical NER.
This module handles the extraction of additional information about entities
from medical knowledge bases like RxNorm.
"""

from typing import List

from ..api.models import Entity, EntityDetail
from ..core.config import settings
from ..core.logging import get_logger

logger = get_logger(__name__)


class EntityLinker:
    """Service for linking extracted entities to medical knowledge bases"""

    def __init__(self, nlp_doc):
        """
        Initialize the linker with a spaCy document

        Args:
            nlp_doc: A processed spaCy document containing entities
        """
        self.doc = nlp_doc
        try:
            self.linker = nlp_doc._.get_pipe("scispacy_linker")
        except (KeyError, AttributeError) as e:
            logger.error(f"scispacy_linker not found in pipeline: {e}")
            self.linker = None

    def extract_entities(self) -> List[Entity]:
        """
        Extract entities from the document and enrich them with linked knowledge

        Returns:
            List[Entity]: A list of extracted entities with their details
        """
        entities = []

        for ent in self.doc.ents:
            umls_entities = self._get_linked_entities(ent)
            entities.append(Entity(text=ent.text, umls_entities=umls_entities))

        return entities

    def _get_linked_entities(self, ent) -> List[EntityDetail]:
        """
        Get linked knowledge base entities for a spaCy entity

        Args:
            ent: A spaCy entity

        Returns:
            List[EntityDetail]: A list of linked entity details
        """
        umls_entities = []

        # Skip if linker is not available
        if self.linker is None:
            return umls_entities

        # Get linked entities if available
        if hasattr(ent._, "kb_ents") and ent._.kb_ents:
            for umls_ent in ent._.kb_ents:
                entity_id = umls_ent[0]
                score = umls_ent[1]

                # Skip low confidence matches
                if score < settings.ENTITY_SCORE_THRESHOLD:
                    continue

                entity_detail = self.linker.kb.cui_to_entity.get(entity_id)

                if entity_detail:
                    umls_entities.append(
                        EntityDetail(
                            canonical_name=entity_detail.canonical_name,
                            definition=getattr(entity_detail, "definition", None),
                            aliases=getattr(entity_detail, "aliases", []),
                        )
                    )

        return umls_entities
