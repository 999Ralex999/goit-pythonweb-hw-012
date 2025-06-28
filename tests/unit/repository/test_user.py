from datetime import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserModel
from app.enum.user_role import UserRole
from app.entity.bootstrap import User
from app.repository.user import UserRepository


@pytest.fixture
def mock_session():
    mock_session = AsyncMock(spec=AsyncSession)
    return mock_session


@pytest.fixture
def user_repository(mock_session):
    return UserRepository(mock_session)


@pytest.fixture
def user():
    return User(
        id=1,
        username="User",
        email="test@test.com",
        password="test",
        email_verified=True,
        refresh_token="refresh_token",
        password_reset_token="password_reset_token",
        avatar="avatar",
        contacts=[],
        role=UserRole.USER,
    )


@pytest.mark.asyncio
async def test_get_by_id(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_id("1")

    assert user is not None
    assert user.id == 1
    assert user.username == "User"
    assert user.email == "test@test.com"
    assert user.password == "test"
    assert user.email_verified == True
    assert user.refresh_token == "refresh_token"
    assert user.password_reset_token == "password_reset_token"
    assert user.avatar == "avatar"
    assert user.contacts == []
    assert user.role == UserRole.USER


@pytest.mark.asyncio
async def test_get_by_id_not_found(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_id(2)

    assert user is None


@pytest.mark.asyncio
async def test_get_by_email(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_email("test@test.com")

    assert user is not None
    assert user.id == 1
    assert user.username == "User"
    assert user.email == "test@test.com"
    assert user.password == "test"
    assert user.email_verified == True
    assert user.refresh_token == "refresh_token"
    assert user.password_reset_token == "password_reset_token"
    assert user.avatar == "avatar"
    assert user.contacts == []
    assert user.role == UserRole.USER


@pytest.mark.asyncio
async def test_get_by_email_not_found(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_email("test@test.com2")

    assert user is None


@pytest.mark.asyncio
async def test_get_by_username(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_username("test@test.com")

    assert user is not None
    assert user.id == 1
    assert user.username == "User"
    assert user.email == "test@test.com"
    assert user.password == "test"
    assert user.email_verified == True
    assert user.refresh_token == "refresh_token"
    assert user.password_reset_token == "password_reset_token"
    assert user.avatar == "avatar"
    assert user.contacts == []
    assert user.role == UserRole.USER


@pytest.mark.asyncio
async def test_get_by_username_not_found(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_username("test@test.com2")

    assert user is None


@pytest.mark.asyncio
async def test_create(user_repository, mock_session):

    model = UserModel(
        username="User",
        email="test@test.com",
        password="testtest",
        avatar="avatar",
        email_verified=True,
        refresh_token="refresh_token",
        password_reset_token="password_reset_token",
        role=UserRole.USER,
    )

    async def add_user_id(user_obj):
        user_obj.id = 1

    mock_session.refresh = AsyncMock(side_effect=add_user_id)

    user = await user_repository.create(model)

    assert isinstance(user, User)
    assert user.id == 1
    assert user.username == "User"
    assert user.email == "test@test.com"
    assert user.password == "testtest"
    assert user.email_verified == True
    assert user.refresh_token == "refresh_token"
    assert user.password_reset_token == "password_reset_token"
    assert user.avatar == "avatar"
    assert user.contacts == []
    assert user.role == UserRole.USER

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_update(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    model = UserModel(
        username="NewUserName",
        email="new_test@test.com",
    )

    user = await user_repository.update(1, model)

    assert isinstance(user, User)
    assert user.id == 1
    assert user.username == "NewUserName"
    assert user.email == "new_test@test.com"
    assert user.password == "test"
    assert user.email_verified == True
    assert user.refresh_token == "refresh_token"
    assert user.password_reset_token == "password_reset_token"
    assert user.avatar == "avatar"
    assert user.contacts == []
    assert user.role == UserRole.USER

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_update_not_found(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    model = UserModel(
        username="NewUserName",
        email="new_test@test.com",
    )

    user = await user_repository.update(2, model)

    assert user is None

    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()
    mock_session.refresh.assert_not_called()


@pytest.mark.asyncio
async def test_delete(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.delete(1)

    mock_session.delete.assert_called_once_with(user)
    mock_session.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_not_found(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    await user_repository.delete(2)

    mock_session.delete.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_create_commit_error(user_repository, mock_session):
    model = UserModel(
        username="User",
        email="test@test.com",
        password="testtest",
        avatar="avatar",
        email_verified=True,
        refresh_token="refresh_token",
        password_reset_token="password_reset_token",
        role=UserRole.USER,
    )

    mock_session.commit = AsyncMock(side_effect=Exception("DB error"))

    with pytest.raises(Exception, match="DB error"):
        await user_repository.create(model)


@pytest.mark.asyncio
async def test_update_with_empty_model(user_repository, mock_session, user):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = user
    mock_session.execute = AsyncMock(return_value=mock_result)

    model = UserModel()  

    updated_user = await user_repository.update(1, model)

    assert updated_user is not None
    assert updated_user.username == "User"  
    assert updated_user.email == "test@test.com"  


@pytest.mark.asyncio
async def test_get_by_email_invalid_format(user_repository, mock_session):
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)

    user = await user_repository.get_by_email("invalid-email")

    assert user is None


@pytest.mark.asyncio
async def test_create_with_minimal_fields(user_repository, mock_session):
    model = UserModel(
        username="MinUser",
        email="min@test.com",
        password="minpass1",  
    )

    async def add_user_id(user_obj):
        user_obj.id = 100

    mock_session.refresh = AsyncMock(side_effect=add_user_id)

    user = await user_repository.create(model)

    assert isinstance(user, User)
    assert user.id == 100
    assert user.username == "MinUser"
    assert user.email == "min@test.com"
    assert user.password == "minpass1"

    mock_session.add.assert_called_once()
    mock_session.commit.assert_awaited_once()
    mock_session.refresh.assert_awaited_once_with(user)

import pytest
from app.schemas.user import UserModel

@pytest.mark.asyncio
async def test_create_invalid_email_format(user_repository, mock_session):
    with pytest.raises(ValueError) as exc_info:
        UserModel(
            username="BadEmailUser",
            email="not-an-email",  
            password="validpass1"
        )

    assert "value is not a valid email address" in str(exc_info.value)
