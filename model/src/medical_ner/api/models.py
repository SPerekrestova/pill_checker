from typing import List, Optional

from pydantic import BaseModel, Field


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


class HealthResponse(BaseModel):
    status: str
    message: str
