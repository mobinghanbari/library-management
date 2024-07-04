import pytest
from fastapi import BackgroundTasks
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base, User
from main import app
from api.users.endpoints import create, confirm_email, reset_password, get_specific_user, update
from api.users.schema.input_chema import UserIn, ChangePassword, UpdateUser
from itsdangerous import URLSafeTimedSerializer

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)

SECRET = "ngyfckmpqvxdsfsdfc"
serializer = URLSafeTimedSerializer(SECRET)


@pytest.fixture(scope="function")
def db():
    """ایجاد یک سشن پایگاه داده برای هر تست"""
    Base.metadata.create_all(bind=engine)  # ایجاد جدول‌ها
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)  # حذف جدول‌ها


def test_create_user(db):
    user_data = UserIn(username="testuser", email="testuser@example.com", phone="12345678901", password="password123")
    background_tasks = BackgroundTasks()

    existing_user = db.query(User).filter_by(email=user_data.email).first()
    if not existing_user:
        user = create(user_data, db, background_tasks)
        assert user.email == "testuser@example.com"
    else:
        assert existing_user.email == user_data.email


def test_confirm_email(db):
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    if not user:
        user = User(username="testuser", email="testuser@example.com", phone="12345678901", password="password123")
        db.add(user)
        db.commit()
        db.refresh(user)
    token = serializer.dumps(user.email, salt='email-confirm')
    confirmed_user = confirm_email(token, db)
    assert confirmed_user.is_activated


def test_reset_password(db):
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    if not user:
        user = User(username="testuser", email="testuser@example.com", phone="12345678901", password="password123")
        db.add(user)
        db.commit()
        db.refresh(user)

    token = serializer.dumps(user.email, salt='reset_password_email')
    password_data = ChangePassword(password="newpassword123", confirm="newpassword123")
    response = reset_password(token, password_data, db)
    assert response["message"] == "Password has been reset successfully"


def test_get_specific_user(db):
    user = db.query(User).filter(User.email == "testuser@example.com").first()
    if not user:
        user = User(username="testuser", email="testuser@example.com", phone="12345678901", password="password123")
        db.add(user)
        db.commit()
        db.refresh(user)

    found_user = get_specific_user(db, user.email).first()
    assert found_user.email == "testuser@example.com"


def test_update_user(db):
    user = User(username="testuser", email="testuser@example.com", phone="12345678901", password="password123")
    db.add(user)
    db.commit()
    db.refresh(user)

    updated_data = UpdateUser(ip_check=True)
    updated_response = update(db, pk=user.id, role="admin", ip_check=updated_data)

    assert updated_response["message"] == "User updated successfully"
