from typing import List, Optional
from datetime import date
from pydantic import BaseModel

# related schema
class Author(BaseModel):
    id: int
    full_name: str
    nationality: str

    class Config:
        orm_mode = True


class Category(BaseModel):
    id: int
    name: str

    class Config:
        orm_mode = True



# returning book with images
class BookWithImage(BaseModel):
    id: int
    title: str
    stock: int
    quantity: int
    published_at: Optional[date]
    images: List[str]
    author: Optional[Author]
    category: Optional[Category]

    class Config:
        orm_mode = True


# output schema
class OuBook(BaseModel):
    id: int
    title: str
    stock: int
    quantity: int
    published_at: Optional[date]
    author: Optional[Author]
    category: Optional[Category]

    class Config:
        orm_mode = True
