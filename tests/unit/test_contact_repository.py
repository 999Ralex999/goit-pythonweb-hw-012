import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from app.repository.contact import ContactRepository
from app.models.contact import Contact
from app.schemas.contact import ContactModel


@pytest.mark.asyncio
async def test_get_contacts_returns_list():
    mock_session = AsyncMock(spec=AsyncSession)
    expected_contacts = [Contact(id=1, first_name="John"), Contact(id=2, first_name="Jane")]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.get_contacts(user_id=1)
    assert result == expected_contacts


@pytest.mark.asyncio
async def test_create_contact_returns_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    contact_data = ContactModel(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890"  
    )
    created_contact = Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="1234567890",
        user_id=1
    )

    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh = AsyncMock()

    repo = ContactRepository(session=mock_session)
    result = await repo.create(contact_data, user_id=1)
    assert result.user_id == 1
    assert result.first_name == "John"



@pytest.mark.asyncio
async def test_delete_contact_success():
    mock_session = AsyncMock(spec=AsyncSession)
    contact_to_delete = Contact(id=1, first_name="John", user_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact_to_delete
    mock_session.execute.return_value = mock_result

    mock_session.delete.return_value = None
    mock_session.commit.return_value = None

    repo = ContactRepository(session=mock_session)
    result = await repo.delete(id=1, user_id=1)
    assert result is True


@pytest.mark.asyncio
async def test_delete_contact_not_found():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.delete(id=99, user_id=1)
    assert result is False


@pytest.mark.asyncio
async def test_get_contacts_by_param():
    mock_session = AsyncMock(spec=AsyncSession)
    param = {"email": "john@example.com"}
    expected_contacts = [Contact(id=1, first_name="John", email="john@example.com", user_id=1)]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.get_contacts_by_param(param=param, user_id=1)
    assert result == expected_contacts


@pytest.mark.asyncio
async def test_get_contacts_with_upcoming_birthdays():
    mock_session = AsyncMock(spec=AsyncSession)
    today = datetime.now().date()

    expected_contacts = [Contact(id=1, first_name="Jane", birthday=today, user_id=1)]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.get_contacts_with_upcoming_birthdays(user_id=1)
    assert result == expected_contacts


@pytest.mark.asyncio
async def test_search_contacts():
    mock_session = AsyncMock(spec=AsyncSession)
    keyword = "Jo"
    expected_contacts = [Contact(id=1, first_name="John", user_id=1)]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.search_contacts(keyword=keyword, user_id=1)
    assert result == expected_contacts


@pytest.mark.asyncio
async def test_paginate_contacts():
    mock_session = AsyncMock(spec=AsyncSession)
    expected_contacts = [Contact(id=1, first_name="John", user_id=1)]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.paginate_contacts(limit=10, offset=0, user_id=1)
    assert result == expected_contacts

@pytest.mark.asyncio
async def test_get_by_id_with_user_id():
    mock_session = AsyncMock(spec=AsyncSession)
    contact = Contact(id=1, first_name="Test", user_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.get_by_id(id=1, user_id=1)

    assert result == contact

@pytest.mark.asyncio
async def test_get_by_email_returns_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    contact = Contact(id=1, email="john@example.com", user_id=1)

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.get_by_email(email="john@example.com", user_id=1)

    assert result == contact
    assert result.email == "john@example.com"

@pytest.mark.asyncio
async def test_update_contact_success():
    mock_session = AsyncMock(spec=AsyncSession)
    contact = Contact(id=1, first_name="John", last_name="Doe", email="john@example.com", phone="123", user_id=1)

    updated_data = ContactModel(first_name="Johnny", last_name="Doe", email="john@example.com", phone="123")

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = contact
    mock_session.execute.return_value = mock_result

    mock_session.add.return_value = None
    mock_session.commit.return_value = None
    mock_session.refresh = AsyncMock()

    repo = ContactRepository(session=mock_session)
    result = await repo.update(id=1, contact_model=updated_data, user_id=1)

    assert result.first_name == "Johnny"
    assert result.last_name == "Doe"
    assert result.email == "john@example.com"

@pytest.mark.asyncio
async def test_query_contacts_by_firstname_and_search():
    mock_session = AsyncMock(spec=AsyncSession)

    from app.schemas.contact import ContactQuery

    query = ContactQuery(
        first_name="John",
        search="ohn",  
        limit=10,
        offset=0
    )

    expected_contacts = [
        Contact(id=1, first_name="John", email="john@example.com", user_id=1)
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.query(query=query, user_id=1)

    assert result == expected_contacts
    assert result[0].first_name == "John"

@pytest.mark.asyncio
async def test_query_contacts_with_birthdays_in_range():
    mock_session = AsyncMock(spec=AsyncSession)
    from app.schemas.contact import ContactQuery

    today = datetime.now().date()
    birthday = today + timedelta(days=5)

    query = ContactQuery(
        birthday_from=today,
        birthday_to=birthday,
        birthday_in_next_days=5,
        limit=10,
        offset=0
    )

    expected_contacts = [
        Contact(id=1, first_name="Jane", birthday=birthday, birthday_of_the_year=birthday.timetuple().tm_yday, user_id=1)
    ]

    mock_scalars = MagicMock()
    mock_scalars.all.return_value = expected_contacts

    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(session=mock_session)
    result = await repo.query(query=query, user_id=1)

    assert result == expected_contacts


