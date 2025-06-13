from typing import List
from fastapi import HTTPException
from app.errors.contact import ContactExistsException
from app.models.contact import Contact
from app.schemas.contact import ContactModel, ContactQuery
from app.repository.contact import ContactRepository


class ContactService:
    """
    Сервіс для роботи з контактами.
    """

    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_by_id(self, id: int, user_id: int | None = None) -> Contact | None:
        """Отримати контакт за ID"""
        return await self.repository.get_by_id(id, user_id)

    async def query(self, query: ContactQuery, user_id: int | None = None) -> List[Contact]:
        """Пошук контактів"""
        return await self.repository.query(query, user_id)

    async def get_closest_birthday(self, days_in: int, limit: int = 10, offset: int = 0, user_id: int | None = None) -> List[Contact]:
        """Контакти з найближчим днем народження"""
        contacts = await self.query(
            ContactQuery(
                limit=limit,
                offset=offset,
                birthday_in_next_days=days_in,
            ),
            user_id,
        )
        return contacts

    async def create(self, contact: ContactModel, user_id: int | None = None) -> Contact:
        """Створити контакт"""
        if await self.repository.get_by_email(contact.email, user_id):
            raise ContactExistsException("Contact with this email already exists")
        return await self.repository.create(contact, user_id)

    async def update(self, id: int, contact: ContactModel, user_id: int | None = None) -> Contact | None:
        """Оновити контакт"""
        return await self.repository.update(id, contact, user_id)

    async def delete(self, id: int, user_id: int | None = None) -> None:
        """Видалити контакт"""
        await self.repository.delete(id, user_id)
