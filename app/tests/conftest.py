import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import User, Role
from app.auth import get_password_hash

TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(
    settings.DATABASE_URL.path,
    settings.DATABASE_URL.path + "_test"
)

engine = create_engine(
    TEST_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    yield db
    db.close()


@pytest.fixture(scope="session")
def test_user(db_session):
    """Create a test user and return it."""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("testpass123"),
        role=Role.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="session")
def client(db_session, test_user):
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as c:
        # Login and get token
        response = c.post(
            "/auth/login",
            data={"username": "testuser", "password": "testpass123"}
        )
        token = response.json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"
        yield c

    app.dependency_overrides.clear()
