import pytest
from httpx import AsyncClient, ASGITransport
from datetime import datetime

from main import app
from app.repository.contact import ContactRepository
from app.schemas.contact import ContactModel

# Дані для створення нового контакту
contact_payload = {
    "first_name": "John",
    "last_name": "Doe",
    "email": "john@example.com",
    "phone": "123456789",
    "birthday": datetime.now().isoformat(),
    "additional_info": "Test contact"
}

@pytest.mark.asyncio
async def test_create_get_update_delete_contact(db_session):
    # Ініціалізуємо репозиторій із реальною сесією
    repo = ContactRepository(db_session)

    # Створення
    contact_model = ContactModel(**contact_payload)
    created = await repo.create(contact_model, user_id=1)
    assert created.email == "john@example.com"

    # Отримання
    fetched = await repo.get_by_id(created.id, user_id=1)
    assert fetched is not None
    assert fetched.id == created.id

    # Оновлення
    updated_payload = contact_payload.copy()
    updated_payload["first_name"] = "Johnny"
    updated_model = ContactModel(**updated_payload)
    updated = await repo.update(created.id, updated_model, user_id=1)
    assert updated.first_name == "Johnny"

    # Видалення
    deleted = await repo.delete(created.id, user_id=1)
    assert deleted is True

    # Перевірка, що контакт видалено
    gone = await repo.get_by_id(created.id, user_id=1)
    assert gone is None




