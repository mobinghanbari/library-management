from datetime import date
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from database.models import Book, Author, Category, BookImage, Borrow, User
from sqlalchemy.exc import IntegrityError


def fetch_books(
        db: Session,
        role,
        category_id: Optional[int] = None,
        user_id: Optional[str] = None,
        filter_date: Optional[date] = None
):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager or  members can see the report"
        )

    # Start with querying the Book model
    books_query = db.query(Book)

    # Apply filters based on optional parameters
    if category_id is not None:
        books_query = books_query.filter(Book.category_id == category_id)
    books_query = books_query.filter(Book.quantity > 0)  # Filter for books with quantity > 0
    books = books_query.all()

    # Fetch borrows based on username and single date
    borrows_query = db.query(Borrow).join(User).join(Book)

    if user_id:
        borrows_query = borrows_query.filter(User.id == user_id)

    if filter_date:
        borrows_query = borrows_query.filter(Borrow.borrow_date == filter_date)

    borrows = borrows_query.all()

    return {
        "count_of_books": len(books),
        "count_of_borrows": len(borrows)
    }
