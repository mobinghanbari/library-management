import os
import shutil
from fastapi import HTTPException, status, UploadFile
from sqlalchemy.orm import Session
from database.models import BookImage, Book
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Read allowed formats and max file size from environment variables
ALLOWED_IMAGE_FORMATS = os.getenv("ALLOWED_IMAGE_FORMATS").split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))


def create(pk: int, file: UploadFile, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager members can add Book Image"
        )

    book = db.query(Book).filter(Book.id == pk).first()

    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The book with given id does not exist"
        )

    # Check file size
    file.file.seek(0, os.SEEK_END)  # Move the cursor to the end of the file
    file_size = file.file.tell()  # Get the current position of the cursor, which is the size of the file
    file.file.seek(0)  # Move the cursor back to the start of the file

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds the maximum allowed size")

    # Check file format
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in ALLOWED_IMAGE_FORMATS:
        raise HTTPException(status_code=400, detail="File format is not supported")

    file_location = f"static/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    image_url = f"/static/{file.filename}"
    book_image = BookImage(book_id=pk, image_url=image_url)
    db.add(book_image)
    db.commit()
    db.refresh(book_image)
    return {"id":book_image.id, "book_id": book.id, "filename": file.filename, "image_url": image_url}


def delete_image(pk: int, role, db: Session):
    if role not in ["admin", "manager"]:
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager members can delete Book Image"
        )

    book_image = db.query(BookImage).filter(BookImage.id == pk).first()
    if not book_image:
        raise HTTPException(status_code=404, detail="Image not found")

    # Delete file from the filesystem
    file_location = book_image.image_url[1:]  # Remove leading slash
    if os.path.exists(file_location):
        os.remove(file_location)

    # Delete record from the database
    db.delete(book_image)
    db.commit()

    return {"detail": "Image deleted successfully"}
