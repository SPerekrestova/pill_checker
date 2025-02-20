from fastapi import Form
from pydantic import BaseModel
from typing import Optional


class ProfileUpdateForm(BaseModel):
    display_name: str
    bio: Optional[str] = None

    @classmethod
    def as_form(
        cls,
        display_name: str = Form(..., description="User's display name"),
        bio: Optional[str] = Form(None, description="User biography (optional)"),
    ):
        return cls(display_name=display_name, bio=bio)
