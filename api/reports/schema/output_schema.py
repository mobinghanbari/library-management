from pydantic import BaseModel
from typing import List, Optional
from datetime import date


class UserSchema(BaseModel):
    id: int
    username: str
    email: str
    phone: str

    class Config:
        orm_mode = True


class CategorySchema(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        orm_mode = True


class AuthorSchema(BaseModel):
    id: int
    full_name: str
    nationality: str

    class Config:
        orm_mode = True


class BookSchema(BaseModel):
    id: int
    title: str
    author: AuthorSchema
    category: Optional[CategorySchema]  # دسته‌بندی به صورت اختیاری
    stock: bool
    quantity: int
    published_at: Optional[date]

    class Config:
        orm_mode = True


class BorrowSchema(BaseModel):
    id: int
    user: UserSchema
    book: BookSchema
    borrow_date: date
    return_date: Optional[date]

    class Config:
        orm_mode = True


class ReportSchema(BaseModel):
    books: List[BookSchema]
    borrows: List[BorrowSchema]
