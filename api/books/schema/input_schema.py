from pydantic import BaseModel, validator
from datetime import date


class InBook(BaseModel):
    title: str
    author_id: int
    category_id: int
    stock: bool
    quantity: int
    published_at: date

    @validator('title')
    def validate_title(cls, v):
        if len(v) < 1 or len(v) > 50:
            raise ValueError('Title must be between 1 and 50 characters long.')
        return v

    @validator('quantity')
    def validate_quantity(cls, v):
        if v < 0:
            raise ValueError('Quantity must be a non-negative integer.')
        return v

    @validator('published_at')
    def validate_published_at(cls, v):
        if v > date.today():
            raise ValueError('Published date cannot be in the future.')
        return v
