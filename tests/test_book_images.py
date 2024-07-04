import os
import shutil

import pytest
from fastapi import HTTPException, UploadFile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from io import BytesIO
from dotenv import load_dotenv
from main import app
from database.connection import get_db
from database.models import Base, Book, BookImage
from api.book_images.endpoints import create, delete_image

# Load environment variables from .env file
load_dotenv()

# تنظیمات پایگاه داده برای تست
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

ALLOWED_IMAGE_FORMATS = os.getenv("ALLOWED_IMAGE_FORMATS").split(",")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE"))


@pytest.fixture(scope="function")
def db_session():
    """ایجاد یک سشن پایگاه داده برای هر تست"""
    Base.metadata.create_all(bind=engine)  # ایجاد جدول‌ها
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)  # حذف جدول‌ها


@pytest.fixture(scope="function", autouse=True)
def setup_static_directory():
    """ایجاد دایرکتوری static برای هر تست و پاکسازی آن بعد از تست"""
    os.makedirs("static", exist_ok=True)
    yield
    shutil.rmtree("static")


def test_create_image(db_session):
    book = Book(title="Test Book", quantity=10, stock=True)
    db_session.add(book)
    db_session.commit()

    file_content = b"this is a test image"
    file = UploadFile(filename="test_image.jpeg", file=BytesIO(file_content))

    result = create(pk=book.id, file=file, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    assert result["book_id"] == book.id
    assert result["filename"] == "test_image.jpeg"
    assert result["image_url"] == "/static/test_image.jpeg"


def test_create_image_invalid_format(db_session):
    book = Book(title="Test Book", quantity=10, stock=True)
    db_session.add(book)
    db_session.commit()

    file_content = b"this is a test image"
    file = UploadFile(filename="test_image.txt", file=BytesIO(file_content))

    with pytest.raises(HTTPException) as excinfo:
        create(pk=book.id, file=file, role="admin", db=db_session)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "File format is not supported"


def test_create_image_exceed_size(db_session):
    book = Book(title="Test Book", quantity=10, stock=True)
    db_session.add(book)
    db_session.commit()

    file_content = b"a" * (MAX_FILE_SIZE + 1)
    file = UploadFile(filename="test_image.png", file=BytesIO(file_content))

    with pytest.raises(HTTPException) as excinfo:
        create(pk=book.id, file=file, role="admin", db=db_session)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "File size exceeds the maximum allowed size"


def test_delete_image(db_session):
    book = Book(title="Test Book", quantity=10, stock=True)
    db_session.add(book)
    db_session.commit()

    file_content = b"this is a test image"
    file = UploadFile(filename="test_image.jpeg", file=BytesIO(file_content))

    result = create(pk=book.id, file=file, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    image_id = result["id"]
    response = delete_image(pk=image_id, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    assert response["detail"] == "Image deleted successfully"

    with pytest.raises(HTTPException) as excinfo:
        delete_image(pk=image_id, role="admin", db=db_session)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Image not found"
