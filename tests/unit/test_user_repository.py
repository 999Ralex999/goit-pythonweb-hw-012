import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user import UserRepository
from app.models import User


@pytest.mark.asyncio
async def test_get_by_email_returns_user():
    # Arrange
    test_email = "test@example.com"
    expected_user = User(id=1, username="test", email=test_email)

    mock_session = AsyncMock(spec=AsyncSession)

    # Правильная цепочка моков
    mock_result = MagicMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=expected_user)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = UserRepository(session=mock_session)

    # Act
    result = await repo.get_by_email(email=test_email)

    # Assert
    assert result == expected_user
