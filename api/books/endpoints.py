from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload
from database.models import Book, Author, Category, BookImage
from sqlalchemy.exc import IntegrityError
from .schema.input_schema import InBook


def create(book: InBook, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can add Book"
        )

    # check if author exist
    author = db.query(Author).filter(Author.id == book.author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )

    # check if category exist
    category = db.query(Category).filter(Category.id == book.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    new_book = Book(
        title=book.title,
        author_id=book.author_id,
        category_id=book.category_id,
        stock=book.stock,
        quantity=book.quantity,
        published_at=book.published_at
    )

    try:
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(detail="Book with this name already exists.", status_code=status.HTTP_400_BAD_REQUEST)

    return new_book


def fetch_books(
        db: Session,
        has_images: Optional[bool] = None,
        in_stock: Optional[bool] = None,
        category_id: Optional[int] = None,
        author_id: Optional[int] = None,
        author_nationality: Optional[str] = None,
        published_year: Optional[int] = None,
        title: Optional[str] = None
):
    query = db.query(Book).options(
        joinedload(Book.images),
        joinedload(Book.author),
        joinedload(Book.category)
    )

    if has_images is not None:
        query = query.filter(Book.images.any() if has_images else ~Book.images.any())

    if in_stock is not None:
        query = query.filter(Book.stock == in_stock)

    if category_id is not None:
        query = query.filter(Book.category_id == category_id)

    if author_id is not None:
        query = query.filter(Book.author_id == author_id)

    if author_nationality is not None:
        query = query.join(Book.author).filter(Author.nationality == author_nationality)

    if published_year is not None:
        query = query.filter(func.extract('year', Book.published_at) == published_year)

    if title is not None:
        query = query.filter(Book.title.ilike(f'%{title}%'))

    books = query.all()

    result = []
    for book in books:
        book_data = {
            "id": book.id,
            "title": book.title,
            "author_id": book.author_id,
            "stock": book.stock,
            "quantity": book.quantity,
            "published_at": book.published_at,
            "images": [image.image_url for image in book.images],
            "author": {
                "id": book.author.id,
                "full_name": book.author.full_name,
                "nationality": book.author.nationality
            } if book.author else None,
            "category": {
                "id": book.category.id,
                "name": book.category.name
            } if book.category else None
        }
        result.append(book_data)

    return result


def update_book(book_id: int, role, book_data: InBook, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can update Book"
        )

    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(detail="Book not found.", status_code=status.HTTP_404_NOT_FOUND)

    author = db.query(Author).filter(Author.id == book_data.author_id).first()
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )

    # check if category exist
    category = db.query(Category).filter(Category.id == book_data.category_id).first()
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    book.title = book_data.title
    book.author_id = book_data.author_id
    book.category_id = book_data.category_id
    book.stock = book_data.stock
    book.quantity = book_data.quantity
    book.published_at = book_data.published_at

    try:
        db.commit()
        db.refresh(book)
    except IntegrityError:
        db.rollback()
        raise HTTPException(detail="Book with this name already exists.", status_code=status.HTTP_400_BAD_REQUEST)

    return book


def delete_book(book_id: int, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can delete Book"
        )
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(detail="Book not found.", status_code=status.HTTP_404_NOT_FOUND)

    db.delete(book)
    db.commit()

    return {"message": "Book deleted successfully."}
