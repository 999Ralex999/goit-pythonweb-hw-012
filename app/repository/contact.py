from datetime import datetime, timedelta
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from app.schemas.contact import ContactModel, ContactQuery
from app.models.contact import Contact


class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_by_id(self, id: int, user_id: int | None = None) -> Contact | None:
        stmt = select(Contact).where(Contact.id == id)
        if user_id:
            stmt = stmt.where(Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str, user_id: int | None = None) -> Contact | None:
        stmt = select(Contact).where(Contact.email == email)
        if user_id:
            stmt = stmt.where(Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_contacts(self, user_id: int) -> List[Contact]:
        stmt = select(Contact).where(Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def create(self, contact: ContactModel, user_id: int | None = None) -> Contact:
        new_contact = Contact(**contact.model_dump(), user_id=user_id)
        self.db.add(new_contact)
        await self.db.commit()
        await self.db.refresh(new_contact)
        return new_contact

    async def update(self, id: int, contact_model: ContactModel, user_id: int | None = None) -> Contact | None:
        contact = await self.get_by_id(id, user_id)
        if contact:
            for key, value in contact_model.model_dump(exclude_unset=True).items():
                setattr(contact, key, value)
            self.db.add(contact)
            await self.db.commit()
            await self.db.refresh(contact)
            return contact
        return None

    async def delete(self, id: int, user_id: int | None = None) -> bool:
        contact = await self.get_by_id(id, user_id)
        if contact:
            await self.db.delete(contact)
            await self.db.commit()
            return True
        return False

    async def get_contacts_by_param(self, param: dict, user_id: int) -> List[Contact]:
        stmt = select(Contact).filter_by(**param).where(Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_contacts_with_upcoming_birthdays(self, user_id: int) -> List[Contact]:
        today = datetime.now().date()
        next_week = today + timedelta(days=7)
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            Contact.birthday.isnot(None),
            Contact.birthday.between(today, next_week)
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def search_contacts(self, keyword: str, user_id: int) -> List[Contact]:
        stmt = select(Contact).where(
            Contact.user_id == user_id,
            or_(
                Contact.first_name.ilike(f"%{keyword}%"),
                Contact.last_name.ilike(f"%{keyword}%"),
                Contact.email.ilike(f"%{keyword}%")
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def paginate_contacts(self, limit: int, offset: int, user_id: int) -> List[Contact]:
        stmt = select(Contact).where(Contact.user_id == user_id).limit(limit).offset(offset)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def query(self, query: ContactQuery, user_id: int | None = None) -> List[Contact]:
        stmt = select(Contact).limit(query.limit).offset(query.offset)
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
            stmt = stmt.where(Contact.birthday >= query.birthday_from)
        if query.birthday_to:
            stmt = stmt.where(Contact.birthday <= query.birthday_to)
        if query.birthday_of_the_year_from:
            stmt = stmt.where(Contact.birthday_of_the_year >= query.birthday_of_the_year_from)
        if query.birthday_of_the_year_to:
            stmt = stmt.where(Contact.birthday_of_the_year <= query.birthday_of_the_year_to)
        if query.birthday_in_next_days:
            today = datetime.now().timetuple().tm_yday
            if today + query.birthday_in_next_days > 365:
                to_day = today + query.birthday_in_next_days - 365
                stmt = stmt.where(
                    (Contact.birthday_of_the_year >= today)
                    | (Contact.birthday_of_the_year <= to_day)
                )
            else:
                to_day = today + query.birthday_in_next_days
                stmt = stmt.where(
                    (Contact.birthday_of_the_year >= today)
                    & (Contact.birthday_of_the_year <= to_day)
                )
        if user_id:
            stmt = stmt.where(Contact.user_id == user_id)
        result = await self.db.execute(stmt)
        return result.scalars().all()



