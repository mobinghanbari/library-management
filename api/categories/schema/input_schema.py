from typing import Optional
from pydantic import BaseModel, validator


class InCategory(BaseModel):
    name: str
    description: str
    parent_id: Optional[int] = None

    @validator('name')
    def validate_name(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Name must be between 1 and 50 characters long.')
        return v

    @validator('description')
    def validate_description(cls, v):
        if len(v) < 1 or len(v) > 250:
            raise ValueError('Description must be between 1 and 250 characters long.')
        return v
