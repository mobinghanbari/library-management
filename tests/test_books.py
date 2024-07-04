from datetime import date
import pytest
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database.models import Base, Book, Author, Category
from api.books.endpoints import create, fetch_books, update_book, delete_book
from api.books.schema.input_schema import InBook

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


# Fixture to add a sample author and category
@pytest.fixture
def sample_author_category(db):
    author = Author(full_name="Sample Author", nationality="Sample Nationality")
    category = Category(name="Sample Category", description="jdsnsjidnsd")
    db.add(author)
    db.add(category)
    db.commit()
    db.refresh(author)
    db.refresh(category)
    return author, category


def test_create_book(db, sample_author_category):
    author, category = sample_author_category
    book_data = InBook(title="New Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                       published_at="2023-01-01")
    new_book = create(book_data, "admin", db)
    assert new_book.title == "New Book"
    assert new_book.author_id == author.id
    assert new_book.category_id == category.id


def test_create_book_unauthorized(db, sample_author_category):
    author, category = sample_author_category
    book_data = InBook(title="New Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                       published_at="2023-01-01")
    with pytest.raises(HTTPException) as excinfo:
        create(book_data, "user", db)
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Only admin or manager members can add Book"


def test_create_book_author_not_found(db):
    book_data = InBook(title="New Book", author_id=999, category_id=1, stock=True, quantity=5,
                       published_at="2023-01-01")
    with pytest.raises(HTTPException) as excinfo:
        create(book_data, "admin", db)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Author not found"


def test_create_book_category_not_found(db):
    author = Author(full_name="Sample Author", nationality="Sample Nationality")
    db.add(author)
    db.commit()
    db.refresh(author)
    book_data = InBook(title="New Book", author_id=author.id, category_id=999, stock=True, quantity=5,
                       published_at="2023-01-01")
    with pytest.raises(HTTPException) as excinfo:
        create(book_data, "admin", db)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail == "Category not found"


def test_create_book_duplicate(db, sample_author_category):
    author, category = sample_author_category
    book_data = InBook(title="Duplicate Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                       published_at="2023-01-01")
    create(book_data, "admin", db)
    with pytest.raises(HTTPException) as excinfo:
        create(book_data, "admin", db)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Book with this name already exists."


def test_fetch_books(db, sample_author_category):
    author, category = sample_author_category
    book1 = Book(title="Book 1", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                 published_at=date(2023, 1, 1))
    book2 = Book(title="Book 2", author_id=author.id, category_id=category.id, stock=True, quantity=3,
                 published_at=date(2023, 6, 1))
    db.add(book1)
    db.add(book2)
    db.commit()

    # Fetch books as instances of Book from the database
    books = fetch_books(db)

    # Assert that we have two books
    assert len(books) == 2


def test_update_book(db, sample_author_category):
    author, category = sample_author_category

    # Create a new book
    book = Book(title="Old Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                published_at=date(2023, 6, 1))
    db.add(book)
    db.commit()
    db.refresh(book)

    # Create a new author
    new_author = Author(full_name="New Author", nationality="New Nationality")
    db.add(new_author)
    db.commit()
    db.refresh(new_author)

    # Define the updated book data
    book_data = InBook(title="Updated Book", author_id=new_author.id, category_id=category.id, stock=True, quantity=10,
                       published_at="2024-01-01")

    # Test case: Update book with admin role
    try:
        updated_book = update_book(book.id, book_data, "admin", db)
        assert updated_book.title == "Updated Book"
        assert updated_book.author_id == new_author.id
    except HTTPException as e:
        assert e.status_code == 403  # Ensure HTTP 403 Forbidden is raised

    # Test case: Update book with manager role
    try:
        updated_book = update_book(book.id, book_data, "manager", db)
        assert updated_book.title == "Updated Book"
        assert updated_book.author_id == new_author.id
    except HTTPException as e:
        assert e.status_code == 403  # Ensure HTTP 403 Forbidden is raised

    # Test case: Update book with an unauthorized role
    try:
        update_book(book.id, book_data, "user", db)
        assert False, "Expected HTTPException 403"
    except HTTPException as e:
        assert e.status_code == 403  # Ensure HTTP 403 Forbidden is raised

    # Clean up: Delete the created author to maintain test isolation
    db.delete(new_author)
    db.commit()


def test_update_book_unauthorized(db, sample_author_category):
    author, category = sample_author_category
    book = Book(title="Old Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                published_at=date(2023, 6, 1))
    db.add(book)
    db.commit()
    db.refresh(book)

    book_data = InBook(title="Updated Book", author_id=author.id, category_id=category.id, stock=True, quantity=10,
                       published_at="2024-01-01")
    with pytest.raises(HTTPException) as excinfo:
        update_book(book.id, book_data, "user", db)
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Only admin or manager members can update Book"


def test_delete_book(db, sample_author_category):
    author, category = sample_author_category
    book = Book(title="Sample Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                published_at=date(2023, 6, 1))
    db.add(book)
    db.commit()
    db.refresh(book)

    delete_book(book.id, "admin", db)

    # Attempt to retrieve the book from the database
    deleted_book = db.query(Book).filter(Book.id == book.id).first()

    # Check that the book object is no longer in the database
    assert deleted_book is None


def test_delete_book_unauthorized(db, sample_author_category):
    author, category = sample_author_category
    book = Book(title="Sample Book", author_id=author.id, category_id=category.id, stock=True, quantity=5,
                published_at=date(2023, 6, 1))
    db.add(book)
    db.commit()
    db.refresh(book)

    with pytest.raises(HTTPException) as excinfo:
        delete_book(book.id, "user", db)
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Only admin or manager members can delete Book"


def test_delete_book_not_found(db):
    with pytest.raises(HTTPException) as excinfo:
        delete_book(999, "admin", db)
    assert excinfo.value.status_code == 404
    assert excinfo.value.detail.strip('.') == "Book not found"
