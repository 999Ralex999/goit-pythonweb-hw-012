import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.user import UserRepository
from app.models import User


@pytest.mark.asyncio
async def test_get_by_email_returns_user():
  
    test_email = "test@example.com"
    expected_user = User(id=1, username="test", email=test_email)

    mock_session = AsyncMock(spec=AsyncSession)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=expected_user)
    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = UserRepository(session=mock_session)

    result = await repo.get_by_email(email=test_email)

    assert result == expected_user

@pytest.mark.asyncio
async def test_get_by_id_returns_user():
    mock_session = AsyncMock(spec=AsyncSession)
    user = User(id=1, username="test", email="test@example.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result

    repo = UserRepository(session=mock_session)
    result = await repo.get_by_id(id=1)

    assert result == user
    assert result.username == "test"

@pytest.mark.asyncio
async def test_get_by_username_returns_user():
    mock_session = AsyncMock(spec=AsyncSession)
    user = User(id=1, username="tester", email="tester@example.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute.return_value = mock_result

    repo = UserRepository(session=mock_session)
    result = await repo.get_by_username(username="tester")

    assert result == user
    assert result.email == "tester@example.com"

@pytest.mark.asyncio
async def test_create_user_success():
    mock_session = AsyncMock(spec=AsyncSession)

    from app.schemas.user import UserModel
    user_data = UserModel(username="newuser", email="new@example.com", password="supersecret")

    created_user = User(id=1, username="newuser", email="new@example.com")

    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh = AsyncMock()

    repo = UserRepository(session=mock_session)
    result = await repo.create(user=user_data)

    assert result.username == "newuser"
    assert result.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_success():
    from app.schemas.user import UserModel
    mock_session = AsyncMock(spec=AsyncSession)

    existing_user = User(id=1, username="old", email="old@example.com")
    updated_model = UserModel(username="new", email="new@example.com", password="supersecurepass")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value = mock_result

    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh = AsyncMock()

    repo = UserRepository(session=mock_session)
    result = await repo.update(id=1, user_model=updated_model)

    assert result.username == "new"
    assert result.email == "new@example.com"


@pytest.mark.asyncio
async def test_delete_user_success():
    mock_session = AsyncMock(spec=AsyncSession)

    existing_user = User(id=1, username="delete", email="del@example.com")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_user
    mock_session.execute.return_value = mock_result

    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    repo = UserRepository(session=mock_session)
    await repo.delete(id=1)

    mock_session.delete.assert_called_once_with(existing_user)
    mock_session.commit.assert_called_once()
