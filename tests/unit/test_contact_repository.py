import pytest
from unittest.mock import AsyncMock
from app.repository.contact import ContactRepository
from app.models.contact import Contact
from app.schemas.contact import ContactModel
from sqlalchemy.ext.asyncio import AsyncSession

@pytest.mark.asyncio
async def test_get_contacts_returns_list():
    mock_session = AsyncMock(spec=AsyncSession)
    expected_contacts = [Contact(id=1, first_name="John"), Contact(id=2, first_name="Jane")]

    mock_scalars = AsyncMock()
    mock_scalars.all = AsyncMock(return_value=expected_contacts)

    mock_result = AsyncMock()
    mock_result.scalars = AsyncMock(return_value=mock_scalars)

    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = ContactRepository(session=mock_session)
    result = await repo.get_contacts(user_id=1)

    assert result == expected_contacts

@pytest.mark.asyncio
async def test_get_contact_by_id_returns_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    expected_contact = Contact(id=1, first_name="John", user_id=1)

    mock_result = AsyncMock()
    mock_result.scalar_one_or_none = AsyncMock(return_value=expected_contact)

    mock_session.execute = AsyncMock(return_value=mock_result)

    repo = ContactRepository(session=mock_session)
    result = await repo.get_by_id(id=1, user_id=1)

    assert result == expected_contact

@pytest.mark.asyncio
async def test_create_contact_returns_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    contact_data = ContactModel(
        first_name="Alice",
        last_name="Smith",
        email="alice@example.com",
        phone="1234567890"
    )
    expected_contact = Contact(**contact_data.model_dump(), id=1, user_id=1)

    # Мокаем методы БД
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    repo = ContactRepository(session=mock_session)
    result = await repo.create(contact=contact_data, user_id=1)

    assert result.first_name == expected_contact.first_name
    assert result.email == expected_contact.email

