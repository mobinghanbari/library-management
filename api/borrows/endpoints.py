from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from database.models import Book, Borrow, User
from sqlalchemy.exc import IntegrityError
from .schema.input_schema import InBorrow
from .schema.output_schema import OuBorrow


def create(borrow: InBorrow, role, db: Session, current_user: User):
    if role not in ["admin", "manager", "user"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager or normal user members can borrow Book"
        )

    # check if book exist
    book = db.query(Book).filter(Book.id == borrow.book_id).first()
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )

    # check if user didn't borrow the book
    borrow_check = db.query(Borrow).filter(Borrow.book_id == borrow.book_id, Borrow.user_id == current_user["id"]).first()
    if borrow_check:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You have already borrowed the book"
        )

    # calculate returning time
    borrow_date = datetime.now().date()
    return_date = borrow_date + timedelta(days=14)

    new_borrow = Borrow(
        user_id=current_user["id"],
        book_id=borrow.book_id,
        return_date=return_date
    )

    if book.quantity > 0:
        db.add(new_borrow)
        book.quantity -= 1
        db.commit()
        db.refresh(new_borrow)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="All the copies of the book are borrowed")

    return new_borrow


def get_all(db: Session, role):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status
            .HTTP_403_FORBIDDEN,
            detail="Only admin or manager  members can see the report"
        )
    borrows = db.query(Borrow).all()
    return borrows


def update(pk: int, db: Session, role: str):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager members can extend borrows."
        )

    borrow = db.query(Borrow).filter(Borrow.id == pk).first()
    if not borrow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Borrow data not found."
        )

    if borrow.return_date is not None:
        borrow.return_date += timedelta(days=7)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot extend borrow without a return date."
        )

    db.commit()
    return borrow
