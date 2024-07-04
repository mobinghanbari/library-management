from pydantic import BaseModel, validator


class InAuthor(BaseModel):
    full_name: str
    nationality: str

    @validator('full_name')
    def validate_full_name(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Full name must be between 1 and 50 characters long.')
        return v

    @validator('nationality')
    def validate_nationality(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Nationality must be between 1 and 50 characters long.')
        return v
