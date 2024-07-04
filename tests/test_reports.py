import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date
from api.reports.endpoints import fetch_books
from database.models import Base, Book, Author, Category, User, Borrow

# Set up a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Define a fixture to provide a test database session
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)

# Define a fixture to provide sample data
@pytest.fixture(scope="function")
def sample_data(db):
    author = Author(full_name="Test Author", nationality="Test Nationality")
    category = Category(name="Test Category", description="ye chizi")
    book1 = Book(title="Test Book 1", author=author, category=category, stock=True, quantity=5,
                 published_at=date(2023, 1, 1))
    book2 = Book(title="Test Book 2", author=author, category=category, stock=True, quantity=3,
                 published_at=date(2023, 6, 1))
    user = User(username="testuser", email="fake@gmail.com", phone="0822634578", password="testpassword")
    borrow = Borrow(user=user, book=book1, borrow_date=date(2023, 6, 1))

    db.add(author)
    db.add(category)
    db.add(book1)
    db.add(book2)
    db.add(user)
    db.add(borrow)
    db.commit()

    return {
        "author": author,
        "category": category,
        "book1": book1,
        "book2": book2,
        "user": user,
        "borrow": borrow,
    }

# Test case for fetch_books function
def test_fetch_books(db, sample_data):
    role = "user"
    books = fetch_books(db, role, category_id=sample_data["category"].id)
    print(books)  # Add this line to print the structure of the returned value
    assert books["count_of_books"] == 2
    assert books["count_of_borrows"] == 1

    # Testing with filter_date
    books_with_date = fetch_books(db, role, category_id=sample_data["category"].id, filter_date=date(2023, 6, 1))
    assert books_with_date["count_of_books"] == 2
    assert books_with_date["count_of_borrows"] == 1

    # Testing with user_id
    books_with_user_id = fetch_books(db, role, user_id=sample_data["user"].id)
    assert books_with_user_id["count_of_books"] == 2
    assert books_with_user_id["count_of_borrows"] == 1

    # Testing with an invalid role
    with pytest.raises(HTTPException) as excinfo:
        fetch_books(db, role="invalid_role")
    assert excinfo.value.status_code == 403
    assert excinfo.value.detail == "Only admin or manager or normal user members can borrow Book"
