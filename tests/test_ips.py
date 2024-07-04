import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from database.models import Base, User, Ip
from api.ips.endpoints import create, get_all, remove
from api.ips.schema.input_schema import InIp

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


def test_create_ip(db_session):
    user = User(username="testuser", email="testuser@example.com", phone="1234567890", password="password")
    db_session.add(user)
    db_session.commit()

    ip_data = InIp(user_id=user.id, ip_address="192.168.1.1")
    new_ip = create(ip=ip_data, role="admin", db=db_session)
    db_session.commit()

    assert new_ip.user_id == user.id
    assert new_ip.ip_address == "192.168.1.1"
    assert new_ip.created_at is not None


def test_get_all_ips(db_session):
    user = User(username="testuser", email="testuser@example.com", phone="1234567890", password="password")
    ip = Ip(user_id=user.id, ip_address="192.168.1.1")
    db_session.add_all([user, ip])
    db_session.commit()

    ips = get_all(role="admin", db=db_session)
    assert len(ips) > 0


def test_remove_ip(db_session):
    user = User(username="testuser", email="testuser@example.com", phone="1234567890", password="password")
    ip = Ip(user_id=user.id, ip_address="192.168.1.1")
    db_session.add_all([user, ip])
    db_session.commit()

    response = remove(pk=ip.id, role="admin", db=db_session)
    db_session.commit()

    assert response["message"] == "The ip has deleted successfully"
    assert db_session.query(Ip).filter(Ip.id == ip.id).first() is None
