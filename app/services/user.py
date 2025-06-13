from libgravatar import Gravatar
from fastapi import BackgroundTasks, File
from app.errors.token import TokenDecodeException
from app.security.tokens import token_encoder
from app.core.config import settings
from app.security.passwords import password_hasher
from app.models.user import User
from app.errors.user import UserExistsException
from app.repository.user import UserRepository
from app.schemas.user import UserModel
from app.schemas.mail import MailModel
from app.services.mail import mail_service
from app.services.upload_file import upload_file_service

class UserService:
    """
    Сервіс для роботи з користувачами.
    """

    def __init__(self, user_repository: UserRepository, background_tasks: BackgroundTasks = BackgroundTasks()):
        self.user_repository = user_repository
        self.background_tasks = background_tasks

    async def get_user_by_email(self, email: str) -> User | None:
        """Отримати користувача за email."""
        return await self.user_repository.get_by_email(email)

    async def get_user_by_username(self, username: str) -> User | None:
        """Отримати користувача за username."""
        return await self.user_repository.get_by_username(username)

    async def create_user(self, user: UserModel) -> User:
        """Створити користувача."""
        user.password = password_hasher.hash_password(user.password)

        if not user.avatar:
            g = Gravatar(user.email)
            user.avatar = g.get_image()

        if await self.get_user_by_email(user.email):
            raise UserExistsException("User with this email already exists")
        if await self.get_user_by_username(user.username):
            raise UserExistsException("User with this username already exists")

        user = await self.user_repository.create(user)
        await self.send_verification_email(user)
        return user

    async def send_verification_email(self, user: User) -> bool:
        """Відправити email для підтвердження."""
        if not user.email_verified:
            self.background_tasks.add_task(
                mail_service.send_email,
                MailModel(
                    to=[user.email],
                    subject="Confirm your email",
                    data={
                        "host": settings.DOMAIN,
                        "username": user.username,
                        "token": await token_encoder.create_token({"sub": user.email}),
                    },
                    template="verify_email.html",
                ),
            )
            return True
        return False

    async def confirm_email(self, token: str) -> bool:
        """Підтвердити email користувача."""
        payload = await token_encoder.decode_token(token)
        email = payload.get("sub")
        if not email:
            raise TokenDecodeException("Token is invalid")
        user = await self.user_repository.get_by_email(email)
        if user and not user.email_verified:
            await self.user_repository.update(user.id, UserModel(email_verified=True))
            return True
        return False

    async def update_avatar(self, user: User, file: File) -> User | None:
        """Оновити аватар користувача."""
        avatar_url = upload_file_service.upload_file(file, user.username)
        return await self.user_repository.update(user.id, UserModel(avatar=avatar_url))

    async def update_refresh_token(self, user: User, refresh_token: str) -> User | None:
        """Оновити refresh токен користувача."""
        return await self.user_repository.update(user.id, UserModel(refresh_token=refresh_token))

