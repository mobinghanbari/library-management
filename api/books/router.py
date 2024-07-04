from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Query
from database.connection import get_db
from sqlalchemy.orm import Session
from auth.ouath2 import get_current_user
from database.models import Category, User
from .schema.input_schema import InBook
from .schema.output_schema import OuBook, BookWithImage
from .endpoints import create, update_book, delete_book, fetch_books
from ..users.utils import validate_token
from dependency.dependency import verify_ip


book_app = APIRouter(prefix="/books", tags=["Book"])


@book_app.get("/list", response_model=List[BookWithImage])
def get_all_books(
        db: Session = Depends(get_db),
        has_images: Optional[bool] = Query(None, description="Enter true to filter books with images, false to filter books without images."),
        in_stock: Optional[bool] = Query(None, description="Enter true to filter books in stock, false to filter books out of stock."),
        category_id: Optional[int] = Query(None, description="Enter the category ID to filter books by category."),
        author_id: Optional[int] = Query(None, description="Enter the author ID to filter books by author."),
        author_nationality: Optional[str] = Query(None, description="Enter the author's nationality to filter books by author's nationality."),
        published_year: Optional[int] = Query(None, description="Enter the published year to filter books by published year."),
        title: Optional[str] = Query(None, description="Enter a part of the title to filter books by title.")
):
    return fetch_books(
        db=db,
        has_images=has_images,
        in_stock=in_stock,
        category_id=category_id,
        author_id=author_id,
        author_nationality=author_nationality,
        published_year=published_year,
        title=title
    )

@book_app.post("/create", response_model=OuBook, dependencies=[Depends(verify_ip)])
def create_book(book: InBook, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return create(book=book, role=current_user["role"], db=db)


@book_app.put("/update/{pk}", response_model=OuBook, dependencies=[Depends(verify_ip)])
def update_book_by_id(pk, data: InBook, db: Session = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return update_book(book_id=pk, role=current_user["role"], book_data=data, db=db)


@book_app.delete("/delete/{pk}", dependencies=[Depends(verify_ip)])
def delete_book_by_id(pk, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    validate_token(current_user)
    return delete_book(book_id=pk, role=current_user["role"], db=db)
