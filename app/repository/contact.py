from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.contact import ContactModel, ContactQuery
from app.entity.contact import Contact


class ContactRepository:
    """
    Repository for managing contacts

    Attributes:
        db (AsyncSession): The database session
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_by_id(self, id: int, user_id: int | None = None) -> Contact | None:
        """
        Get contact by ID

        Args:
            id (int): The ID of the contact
            user_id (int | None): The ID of the user

        Returns:
            Contact | None: The contact if found, None otherwise
        """
        stmt = select(Contact).where(Contact.id == id)
        if user_id:
            stmt = stmt.where(Contact.user_id == user_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(
        self, email: str, user_id: int | None = None
    ) -> Contact | None:
        """
        Get contact by email

        Args:
            email (str): The email of the contact
            user_id (int | None): The ID of the user

        Returns:
            Contact | None: The contact if found, None otherwise
        """
        stmt = select(Contact).where(Contact.email == email)
        if user_id:
            stmt = stmt.where(Contact.user_id == user_id)

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self, contact: ContactModel, user_id: int | None = None
    ) -> Contact:
        """
        Create contact

        Args:
            contact (ContactModel): The contact to create
            user_id (int | None): The ID of the user

        Returns:
            Contact: The created contact
        """
        new_contact = Contact(**contact.model_dump(), user_id=user_id)
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return new_contact

    async def update(
        self, id: int, contact_model: ContactModel, user_id: int | None = None
    ) -> Contact | None:
        """
        Update contact

        Args:
            id (int): The ID of the contact
            contact_model (ContactModel): The contact to update
            user_id (int | None): The ID of the user

        Returns:
            Contact | None: The updated contact if found, None otherwise
        """
        contact = await self.get_by_id(id, user_id)

        if contact:
            for key, value in contact_model.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)

            self.db.add(contact)
            await self.db.commit()
            await self.db.refresh(contact)
            return contact

        return None

    async def delete(self, id: int, user_id: int | None = None) -> None:
        """
        Delete contact by ID

        Args:
            id (int): The ID of the contact
            user_id (int | None): The ID of the user

        Returns:
            None
        """
        contact = await self.get_by_id(id, user_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()

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
        stmt = select(Contact)
        stmt = stmt.limit(query.limit)
        stmt = stmt.offset(query.offset)

        if query.first_name:
            stmt = stmt.where(Contact.first_name == query.first_name)

        if query.last_name:
            stmt = stmt.where(Contact.last_name == query.last_name)

        if query.email:
            stmt = stmt.where(Contact.email == query.email)

        if query.phone:
            stmt = stmt.where(Contact.phone == query.phone)

        if query.search:
            stmt = stmt.where(
                Contact.first_name.ilike(f"%{query.search}%")
                | Contact.last_name.ilike(f"%{query.search}%")
                | Contact.email.ilike(f"%{query.search}%")
            )

        if query.birthday_from:
            stmt = stmt.where(Contact._birthday >= query.birthday_from)

        if query.birthday_to:
            stmt = stmt.where(Contact._birthday <= query.birthday_to)

        if query.birthday_of_the_year_from:
            stmt = stmt.where(
                Contact._birthday_of_the_year >= query.birthday_of_the_year_from
            )

        if query.birthday_of_the_year_to:
            stmt = stmt.where(
                Contact._birthday_of_the_year <= query.birthday_of_the_year_to
            )

        if query.birthday_in_next_days:
            today = datetime.now().timetuple().tm_yday
            if today + query.birthday_in_next_days > 365:
                to_day = today + query.birthday_in_next_days - 365
                stmt = stmt.where(
                    (Contact._birthday_of_the_year >= today)
                    | (Contact._birthday_of_the_year <= to_day)
                )
            else:
                to_day = today + query.birthday_in_next_days
                stmt = stmt.where(
                    (Contact._birthday_of_the_year >= today)
                    & (Contact._birthday_of_the_year <= to_day)
                )

        if user_id:
            stmt = stmt.where(Contact.user_id == user_id)

        result = await self.db.execute(stmt)
        return result.scalars().all()
