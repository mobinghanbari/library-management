from fastapi import HTTPException, status
from sqlalchemy.orm import Session, joinedload
from database.models import Author, Book
from sqlalchemy.exc import IntegrityError
from .schema.input_schema import InAuthor


def create(author: InAuthor, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can add Author"
        )

    new_author = Author(
        full_name=author.full_name,
        nationality=author.nationality
    )

    try:
        db.add(new_author)
        db.commit()
        db.refresh(new_author)
    except IntegrityError:
        db.rollback()
        raise HTTPException(detail="Author with this name already exists.", status_code=status.HTTP_400_BAD_REQUEST)

    return new_author


def get_author_by_id(author_id: int, db: Session):
    authors = db.query(Author).filter(Author.id == author_id).first()

    if not authors:
        raise HTTPException(detail="The author does not exist", status_code=status.HTTP_404_NOT_FOUND)

    return authors


def get_all_authors(db: Session):
    return db.query(Author).all()


def update_author(author_id: int, role, author_data: InAuthor, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can update Author"
        )

    author = db.query(Author).filter(Author.id == author_id).first()
    if not author:
        raise HTTPException(detail="Author not found.", status_code=status.HTTP_404_NOT_FOUND)

    author.full_name = author_data.full_name
    author.nationality = author.nationality

    try:
        db.commit()
        db.refresh(author)
    except IntegrityError:
        db.rollback()
        raise HTTPException(detail="Author with this name already exists.", status_code=status.HTTP_400_BAD_REQUEST)

    return author


def delete_author(author_id: int, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can delete Author"
        )
    author = db.query(Author).filter(Author.id == author_id).first()
    book = db.query(Book).filter(Book.author_id == author_id).first()
    if not author:
        raise HTTPException(detail="Author not found.", status_code=status.HTTP_404_NOT_FOUND)

    if book:
        raise HTTPException(detail="Author who has a book can't be delete.", status_code=status.HTTP_400_BAD_REQUEST)

    db.delete(author)
    db.commit()

    return {"message": "Author deleted successfully."}
