import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import SessionLocal
from app.models.user import User
from main import app
from app.services.auth import get_current_user


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@pytest.fixture
def test_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        email_verified=True
    )


# 👉 Подмена Depends(get_current_user)
async def override_get_current_user():
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        email_verified=True
    )

app.dependency_overrides[get_current_user] = override_get_current_user



