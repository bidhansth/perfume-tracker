import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.database import Base, get_db
from app.config import settings
from app.models import User, Role
from app.auth import get_password_hash

TEST_DATABASE_URL = str(settings.DATABASE_URL).replace(
    settings.DATABASE_URL.path,
    settings.DATABASE_URL.path + "_test"
)

engine = create_async_engine(
    TEST_DATABASE_URL,
    pool_size=5,
    max_overflow=10,
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


@pytest_asyncio.fixture(scope="session")
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def test_user(db_session):
    """Create a test user and return it."""
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("testpass123"),
        role=Role.USER,
        is_active=True
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="session")
async def client(db_session, test_user):
    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        # Login and get token
        response = await c.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpass123"}
        )
        token = response.json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"
        yield c

    app.dependency_overrides.clear()
