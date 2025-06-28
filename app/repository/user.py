from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.entity.user import User
from app.schemas.user import UserModel


class UserRepository:
    """
    Repository for managing users

    Attributes:
        db (AsyncSession): The database session
    """

    def __init__(self, session: AsyncSession):
        self.db = session

    async def get_by_id(self, id: int) -> User | None:
        """
        Get user by ID

        Args:
            id (int): The ID of the user

        Returns:
            User | None: The user if found, None otherwise
        """
        stmt = select(User).where(User.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Get user by email

        Args:
            email (str): The email of the user

        Returns:
            User | None: The user if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        """
        Get user by username

        Args:
            username (str): The username of the user

        Returns:
            User | None: The user if found, None otherwise
        """
        stmt = select(User).where(User.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, user: UserModel) -> User:
        """
        Create user

        Args:
            user (UserModel): The user to create

        Returns:
            User: The created user
        """
        new_user = User(**user.model_dump())
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def update(self, id: int, user_model: UserModel) -> User | None:
        """
        Update user

        Args:
            id (int): The ID of the user
            user_model (UserModel): The user to update

        Returns:
            User | None: The updated user if found, None otherwise
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
        Delete user

        Args:
            id (int): The ID of the user

        Returns:
            None
        """
        user = await self.get_by_id(id)
        if user:
            await self.db.delete(user)
            await self.db.commit()
