import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """
    Асинхронна фікстура, яка створює сесію бази даних через async with get_db().
    """
    async with get_db() as session:
        yield session


@pytest.fixture
def test_user():
    """
    Фікстура тестового користувача.
    """
    return User(
        id=1,
        username="testuser",
        email="test@example.com",
        email_verified=True
    )


