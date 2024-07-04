import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from database.models import Base, Author
from api.authors.endpoints import create, get_author_by_id, get_all_authors, update_author, delete_author
from api.authors.schema.input_schema import InAuthor

# Set up a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database schema
Base.metadata.create_all(bind=engine)


# Fixture to get a new database session for each test
@pytest.fixture(scope="function")
def db():
    """ایجاد یک سشن پایگاه داده برای هر تست"""
    Base.metadata.create_all(bind=engine)  # ایجاد جدول‌ها
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)  # حذف جدول‌ها


# Fixture to add a sample author
@pytest.fixture
def sample_author(db):
    author = Author(full_name="Sample Author", nationality="Sample Nationality")
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


def test_create_author(db):
    author_data = InAuthor(full_name="New Author", nationality="New Nationality")
    new_author = create(author_data, "admin", db)
    assert new_author.full_name == "New Author"
    assert new_author.nationality == "New Nationality"


def test_create_author_unauthorized(db):
    author_data = InAuthor(full_name="New Author", nationality="New Nationality")
    with pytest.raises(HTTPException) as excinfo:
        create(author_data, "user", db)
    assert excinfo.value.status_code == 403


def test_get_author_by_id(db, sample_author):
    retrieved_author = get_author_by_id(sample_author.id, db)
    assert retrieved_author.full_name == "Sample Author"


def test_get_author_by_id_not_found(db):
    with pytest.raises(HTTPException) as excinfo:
        get_author_by_id(999, db)
    assert excinfo.value.status_code == 404


def test_get_all_authors(db, sample_author):
    authors = get_all_authors(db)
    assert len(authors) == 1
    assert authors[0].full_name == "Sample Author"


def test_update_author(db, sample_author):
    author_data = InAuthor(full_name="Updated Author", nationality="Updated Nationality")
    updated_author = update_author(sample_author.id, "admin", author_data, db)
    assert updated_author.full_name == "Updated Author"


def test_update_author_not_found(db):
    author_data = InAuthor(full_name="Nonexistent Author", nationality="Nonexistent Nationality")
    with pytest.raises(HTTPException) as excinfo:
        update_author(999, "admin", author_data, db)
    assert excinfo.value.status_code == 404


def test_delete_author(db, sample_author):
    delete_author(sample_author.id, "admin", db)
    with pytest.raises(HTTPException) as excinfo:
        get_author_by_id(sample_author.id, db)
    assert excinfo.value.status_code == 404


def test_delete_author_not_found(db):
    with pytest.raises(HTTPException) as excinfo:
        delete_author(999, "admin", db)
    assert excinfo.value.status_code == 404
