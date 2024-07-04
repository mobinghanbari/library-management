from pydantic import BaseModel, validator


class InBorrow(BaseModel):
    book_id: int

    @validator('book_id')
    def validate_book_id(cls, v):
        if v <= 0:
            raise ValueError('Book ID must be a positive integer.')
        return v
