from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedSchema(BaseSchema):
    """Base schema with timestamp fields."""

    created_at: datetime = datetime.utcnow()
    updated_at: Optional[datetime] = None
