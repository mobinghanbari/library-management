import pytest
from fastapi import HTTPException, status
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from api.chang_roles.endpoints import update
from database.models import Base, User, Role
from api.chang_roles.schema.input_schema import UpdateUserRole

# Set up a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Define a fixture to provide a test database session
@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)  # Create tables
    session = TestingSessionLocal()
    yield session
    session.rollback()
    session.close()
    Base.metadata.drop_all(bind=engine)  # Drop tables


# Define a fixture to provide sample data
@pytest.fixture(scope="function")
def sample_data(db):
    admin_role = Role(slug="admin")
    user_role = Role(slug="user")
    user = User(username="testuser", email="test@example.com", phone="1234567890", password="testpassword",
                role=admin_role)

    db.add(admin_role)
    db.add(user_role)
    db.add(user)
    db.commit()

    return {
        "admin_role": admin_role,
        "user_role": user_role,
        "user": user,
    }


# Test case for the update function
def test_update_role(db, sample_data):
    user = sample_data["user"]
    new_role_data = UpdateUserRole(role="user")

    # Perform the update
    response = update(pk=user.id, role="admin", new_role=new_role_data, db=db)

    # Fetch the updated user from the database
    updated_user = db.query(User).filter(User.id == user.id).first()

    assert response["message"] == f"The role of {updated_user.username} has been changed to user"
    assert updated_user.role.slug == "user"

    # Test for non-admin role attempting the update
    with pytest.raises(HTTPException) as excinfo:
        update(pk=user.id, role="user", new_role=new_role_data, db=db)
    assert excinfo.value.status_code == status.HTTP_403_FORBIDDEN
    assert excinfo.value.detail == "Only admin members can change User Role"

    # Test for non-existing user
    with pytest.raises(HTTPException) as excinfo:
        update(pk=9999, role="admin", new_role=new_role_data, db=db)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "User not found"

    # Test for non-existing role in the database
    new_role_data_invalid = UpdateUserRole(
        role="manager")  # Assuming 'manager' is a valid role but not added to the sample data
    with pytest.raises(HTTPException) as excinfo:
        update(pk=user.id, role="admin", new_role=new_role_data_invalid, db=db)
    assert excinfo.value.status_code == status.HTTP_404_NOT_FOUND
    assert excinfo.value.detail == "Role not found"
