from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserModel

class UserRepository:
    """
    Репозиторій для роботи з користувачами у базі даних.
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_by_id(self, id: int) -> User | None:
        """
        Отримати користувача за ID.
        """
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Отримати користувача за email.
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return await result.scalar_one_or_none()  


    async def get_by_username(self, username: str) -> User | None:
        """
        Отримати користувача за username.
        """
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: UserModel) -> User:
        """
        Створити нового користувача.
        """
        new_user = User(**user.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, id: int, user_model: UserModel) -> User | None:
        """
        Оновити користувача.
        """
        user = await self.get_by_id(id)
        if user:
            for key, value in user_model.model_dump(exclude_unset=True).items():
                setattr(user, key, value)
            self.db.add(user)
            await self.db.commit()
            await self.db.refresh(user)
            return user
        return None

    async def delete(self, id: int) -> None:
        """
        Видалити користувача за id.
        """
        user = await self.get_by_id(id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
