from datetime import datetime, timedelta
from http.client import HTTPException
from typing import List
from app.exceptions.contact_exists_exception import ContactExistsException
from app.entity.contact import Contact
from app.schemas.contact import ContactModel, ContactQuery
from app.repository.contact import ContactRepository


class ContactService:
    """
    Service for managing contacts

    Attributes:
        repository (ContactRepository): The repository for managing contacts
    """

    def __init__(self, repository: ContactRepository):
        self.repository = repository

    async def get_by_id(self, id: int, user_id: int | None = None) -> Contact | None:
        """
        Get a contact by ID

        Args:
            id (int): The ID of the contact
            user_id (int | None): The ID of the user

        Returns:
            Contact | None: The contact if found, None otherwise
        """
        return await self.repository.get_by_id(id, user_id)

    async def query(
        self, query: ContactQuery, user_id: int | None = None
    ) -> List[Contact]:
        """
        Query contacts

        Args:
            query (ContactQuery): The query to filter contacts
            user_id (int | None): The ID of the user

        Returns:
            List[Contact]: The list of contacts
        """
        return await self.repository.query(query, user_id)

    async def get_closest_birthday(
        self, days_in: int, limit: int = 10, offset: int = 0, user_id: int | None = None
    ) -> List[Contact]:
        """
        Get contacts with closest birthday in the next n days

        Args:
            days_in (int): The number of days in the future to get contacts with closest birthday
            limit (int): The limit of contacts to return
            offset (int): The offset of the contacts to return
            user_id (int | None): The ID of the user

        Returns:
            List[Contact]: The list of contacts with closest birthday
        """
        contacts = await self.query(
            ContactQuery(
                limit=limit,
                offset=offset,
                birthday_in_next_days=days_in,
            ),
            user_id,
        )
        return contacts

    async def create(
        self, contact: ContactModel, user_id: int | None = None
    ) -> Contact:
        """
        Create a contact

        Args:
            contact (ContactModel): The contact to create
            user_id (int | None): The ID of the user

        Returns:
            Contact: The created contact
        """
        if await self.repository.get_by_email(contact.email, user_id):
            raise ContactExistsException("Contact with this email already exists")
        return await self.repository.create(contact, user_id)

    async def update(
        self, id: int, contact: ContactModel, user_id: int | None = None
    ) -> Contact | None:
        """
        Update a contact

        Args:
            id (int): The ID of the contact
            contact (ContactModel): The contact to update
            user_id (int | None): The ID of the user

        Returns:
            Contact | None: The updated contact if found, None otherwise
        """
        return await self.repository.update(id, contact, user_id)

    async def delete(self, id: int, user_id: int | None = None) -> None:
        """
        Delete a contact

        Args:
            id (int): The ID of the contact
            user_id (int | None): The ID of the user

        Returns:
            None
        """
        await self.repository.delete(id, user_id)
