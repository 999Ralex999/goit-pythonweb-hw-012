import logging
from typing import TYPE_CHECKING
from libgravatar import Gravatar
from fastapi import BackgroundTasks, File

from app.constant_bag.redis import RedisKey
from app.exceptions.token_decode_exception import TokenDecodeException
from app.security.token_encoder import token_encoder
from app.conf.config import settings
from app.security.password_hasher import password_hasher
from app.entity.user import User
from app.exceptions.user_exists_exception import UserExistsException
from app.repository.user import UserRepository
from app.schemas.user import UserModel
from app.schemas.mail import MailModel
from app.services.mail import mail_service
from app.services.upload_file import upload_file_service
from app.database.redis import invalidate, invalidate_cache
from app.services.auth import auth_service


logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


class UserService:
    """
    Service for managing users

    Attributes:
        user_repository (UserRepository): The repository for managing users
        background_tasks (BackgroundTasks): The background tasks for the user service
    """

    def __init__(
        self,
        user_repository: UserRepository,
        background_tasks: BackgroundTasks = BackgroundTasks(),
    ):
        self.user_repository = user_repository
        self.background_tasks = background_tasks

    @staticmethod
    async def invalidate_user_cache(user: User | None):
        """
        Invalidate the cache for a user

        Args:
            user (User): The user to invalidate the cache for
        """
        if user:
            await invalidate(RedisKey.AUTH_USER.format(username=user.username))

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Get a user by email

        Args:
            email (str): The email of the user

        Returns:
            User | None: The user if found, None otherwise
        """
        return await self.user_repository.get_by_email(email)

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Get a user by username

        Args:
            username (str): The username of the user

        Returns:
            User | None: The user if found, None otherwise
        """
        return await self.user_repository.get_by_username(username)

    @invalidate_cache(invalidator_function=invalidate_user_cache)
    async def create_user(self, user: UserModel) -> User:
        """
        Create a user

        Args:
            user (UserModel): The user to create

        Returns:
            User: The created user
        """

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
        """
        Send a verification email to a user

        Args:
            user (User): The user to send the verification email to

        Returns:
            bool: True if the verification email was sent, False otherwise
        """
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

    async def send_password_reset_email(self, user: User) -> bool:
        """
        Send a verification email to a user

        Args:
            user (User): The user to send the verification email to

        Returns:
            bool: True if the verification email was sent, False otherwise
        """
        if user.email_verified:
            self.background_tasks.add_task(
                mail_service.send_email,
                MailModel(
                    to=[user.email],
                    subject="Password reset",
                    data={
                        "host": settings.DOMAIN,
                        "username": user.username,
                        "token": user.password_reset_token,
                    },
                    template="reset_password.html",
                ),
            )
            return True
        return False

    @invalidate_cache(invalidator_function=invalidate_user_cache)
    async def confirm_email(self, token: str) -> User:
        """
        Confirm a user's email

        Args:
            token (str): The token to confirm the email

        Returns:
            bool: True if the email was confirmed, False otherwise
        """
        payload = await token_encoder.decode_token(token)
        email = payload.get("sub")

        if not email:
            raise TokenDecodeException("Token is invalid")

        user = await self.user_repository.get_by_email(email)

        if user and not user.email_verified:
            await self.user_repository.update(
                user.id,
                UserModel(email_verified=True),
            )
            return user
        return user

    @invalidate_cache(invalidator_function=invalidate_user_cache)
    async def update_avatar(self, user: User, file: File) -> User | None:
        """
        Update a user's avatar

        Args:
            user (User): The user to update the avatar for
            file (File): The file to update the avatar with

        Returns:
            User | None: The updated user if found, None otherwise
        """
        avatar_url = upload_file_service.upload_file(file, user.username)
        return await self.user_repository.update(user.id, UserModel(avatar=avatar_url))

    @invalidate_cache(invalidator_function=invalidate_user_cache)
    async def update_refresh_token(self, user: User, refresh_token: str) -> User | None:
        """
        Update a user's refresh token

        Args:
            user (User): The user to update the refresh token for
            refresh_token (str): The refresh token to update

        Returns:
            User | None: The updated user if found, None otherwise
        """
        return await self.user_repository.update(
            user.id, UserModel(refresh_token=refresh_token)
        )

    @invalidate_cache(invalidator_function=invalidate_user_cache)
    async def request_password_reset(self, email: str) -> User | None:
        """
        Request a password reset

        Args:
            email (str): The email of the user to request a password reset for

        Returns:
            bool: True if the password reset was requested, False otherwise
        """
        user = await self.user_repository.get_by_email(email)
        if user:
            password_reset_token = await auth_service.create_password_reset_token(user)
            user = await self.user_repository.update(
                user.id, UserModel(password_reset_token=password_reset_token)
            )
            await self.send_password_reset_email(user)
            logging.info(f"Password reset email sent to {email}")
        else:
            logging.info(f"Password reset email not sent to {email}")

        return user

    @invalidate_cache(invalidator_function=invalidate_user_cache)
    async def reset_password(self, user: User, password: str) -> User | None:
        """
        Update a user's password

        Args:
            user (User): The user to reset the password for
            password (str): The new password

        Returns:
            User | None: The updated user if found, None otherwise
        """
        return await self.user_repository.update(
            user.id,
            UserModel(
                password=password_hasher.hash_password(password),
                password_reset_token=None,
            ),
        )
