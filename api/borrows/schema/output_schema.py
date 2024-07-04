from typing import Optional

from pydantic import BaseModel
from datetime import date


class User(BaseModel):
    id: int
    username: str

    class Config:
        orm_mode = True


class Book(BaseModel):
    id: int
    title: str

    class Config:
        orm_mode = True


class OuBorrow(BaseModel):
    id: int
    borrow_date: Optional[date]
    return_date: Optional[date]
    user: Optional[User]
    book: Optional[Book]

    class Config:
        orm_mode = True
