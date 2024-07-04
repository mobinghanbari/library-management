import pytest
from fastapi import HTTPException, BackgroundTasks
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database.connection import get_db
from database.models import Base, Category
from api.categories.schema.input_schema import InCategory
from api.categories.endpoints import create, get_category_by_id, get_all_categories, update_category, delete_category

# تنظیمات پایگاه داده برای تست
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

client = TestClient(app)


@pytest.fixture(scope="function")
def db_session():
    """ایجاد یک سشن پایگاه داده برای هر تست"""
    Base.metadata.create_all(bind=engine)  # ایجاد جدول‌ها
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)  # حذف جدول‌ها


def test_create_category(db_session):
    category_data = InCategory(name="Test Category", description="Test Description", parent_id=None)
    new_category = create(category=category_data, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها
    assert new_category.name == "Test Category"
    assert new_category.description == "Test Description"


def test_get_category_by_id(db_session):
    category_data = InCategory(name="Test Category", description="Test Description", parent_id=None)
    new_category = create(category=category_data, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    fetched_category = get_category_by_id(category_id=new_category.id, db=db_session)
    assert fetched_category.name == "Test Category"
    assert fetched_category.description == "Test Description"


def test_get_all_categories(db_session):
    category_data = InCategory(name="Test Category", description="Test Description", parent_id=None)
    create(category=category_data, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    categories = get_all_categories(db=db_session)
    assert len(categories) > 0


def test_update_category(db_session):
    category_data = InCategory(name="Test Category", description="Test Description", parent_id=None)
    new_category = create(category=category_data, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    updated_data = InCategory(name="Updated Category", description="Updated Description", parent_id=None)
    updated_category = update_category(category_id=new_category.id, role="admin", category_data=updated_data,
                                       db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    assert updated_category.name == "Updated Category"
    assert updated_category.description == "Updated Description"


def test_delete_category(db_session):
    category_data = InCategory(name="Test Category", description="Test Description", parent_id=None)
    new_category = create(category=category_data, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها

    response = delete_category(category_id=new_category.id, role="admin", db=db_session)
    db_session.commit()  # ذخیره کردن داده‌ها
    assert response["message"] == "Category deleted successfully."

    with pytest.raises(HTTPException) as excinfo:
        get_category_by_id(category_id=new_category.id, db=db_session)
    assert excinfo.value.status_code == 404
