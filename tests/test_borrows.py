import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
from main import app
from database.connection import get_db
from database.models import Base, User, Book, Borrow
from api.borrows.endpoints import create, get_all, update
from api.borrows.schema.input_schema import InBorrow

# Database settings for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """Create a database session for each test."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_create_borrow(db_session):
    user = User(username="testuser", email="testuser@example.com", phone="1234567890", password="password")
    book = Book(title="Test Book", quantity=10, stock=True)
    db_session.add_all([user, book])
    db_session.commit()

    borrow_data = InBorrow(book_id=book.id)
    current_user = {"id": user.id}
    new_borrow = create(borrow=borrow_data, role="user", db=db_session, current_user=current_user)
    db_session.commit()

    assert new_borrow.user_id == user.id
    assert new_borrow.book_id == book.id
    assert new_borrow.return_date == datetime.now().date() + timedelta(days=14)
    assert book.quantity == 9


def test_get_all_borrows(db_session):
    user = User(username="testuser", email="testuser@example.com", phone="1234567890", password="password")
    book = Book(title="Test Book", quantity=10, stock=True)
    borrow = Borrow(user_id=user.id, book_id=book.id, return_date=datetime.now().date() + timedelta(days=14))
    db_session.add_all([user, book, borrow])
    db_session.commit()

    borrows = get_all(db=db_session, role="admin")
    assert len(borrows) > 0


def test_update_borrow(db_session):
    user = User(username="testuser", email="testuser@example.com", phone="1234567890", password="password")
    book = Book(title="Test Book", quantity=10, stock=True)
    borrow = Borrow(user_id=user.id, book_id=book.id, return_date=datetime.now().date() + timedelta(days=14))
    db_session.add_all([user, book, borrow])
    db_session.commit()

    updated_borrow = update(pk=borrow.id, db=db_session, role="admin")
    db_session.commit()

    assert updated_borrow.return_date == datetime.now().date() + timedelta(days=21)
