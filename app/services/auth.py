import logging
from typing import TYPE_CHECKING
from fastapi import Depends, HTTPException, status
from jose import JWTError
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
    OAuth2PasswordBearer,
)
from sqlalchemy.orm import Session

from app.constant_bag.redis import RedisKey
from app.exceptions.token_decode_exception import TokenDecodeException
from app.security.password_hasher import password_hasher
from app.entity.user import User
from app.enum.user_role import UserRole
from app.security.constant_bag.token_types import TokenTypes
from app.repository.user import UserRepository
from app.database.db import get_db
from app.security.token_encoder import token_encoder
from app.conf.config import settings
from app.database.redis import cache


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    description="OAuth2 with Password (and hashing), Bearer with JWT tokens",
)

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


class AuthService:
    """
    Service for managing authentication
    """

    async def create_access_token(self, user: User) -> str:
        """
        Create an access token

        Args:
            user (User): The user to create an access token for

        Returns:
            str: The access token
        """
        payload = {
            "sub": user.username,
            "type": TokenTypes.ACCESS,
        }
        return await token_encoder.create_token(payload)

    async def create_refresh_token(self, user: User) -> str:
        """
        Create a refresh token

        Args:
            user (User): The user to create a refresh token for

        Returns:
            str: The refresh token
        """
        payload = {
            "sub": user.username,
            "type": TokenTypes.REFRESH,
        }
        return await token_encoder.create_token(
            payload,
            expires_delta=settings.JWT_REFRESH_EXPIRATION_SECONDS,
        )

    async def create_password_reset_token(self, user: User) -> str:
        """
        Create a password reset token

        Args:
            user (User): The user to create a password reset token for

        Returns:
            str: The password reset token
        """
        payload = {
            "sub": user.email,
            "type": TokenTypes.PASSWORD_RESET,
        }
        return await token_encoder.create_token(payload, expires_delta=3600)

    async def verify_password_reset_token(self, token: str, db: Session) -> User | None:
        """
        Verify a password reset token

        Args:
            token (str): The password reset token
            db (Session): The database session

        Returns:
            User | None: The user if the token is valid, None otherwise
        """
        payload = await token_encoder.decode_token(token)
        email = payload.get("sub")

        if payload.get("type") != TokenTypes.PASSWORD_RESET or email is None:
            raise TokenDecodeException(
                "Invalid token",
            )

        user_repository = UserRepository(db)
        user = await user_repository.get_by_email(email)

        if not user or user.password_reset_token != token:
            raise TokenDecodeException("Invalid token")

        return user

    async def verify_refresh_token(self, refresh_token: str, db: Session) -> User:
        """
        Verify a refresh token

        Args:
            refresh_token (str): The refresh token
            db (Session): The database session

        Returns:
            User: The user if the token is valid
        """
        payload = await token_encoder.decode_token(refresh_token)
        username = payload.get("sub")
        if payload.get("type") != TokenTypes.REFRESH or username is None:
            raise TokenDecodeException(
                "Invalid refresh token",
            )
        user_repository = UserRepository(db)
        user = await user_repository.get_by_username(username)
        if not user:
            raise TokenDecodeException(
                "User not found",
            )
        if user.refresh_token != refresh_token:
            raise TokenDecodeException(
                "Invalid refresh token",
            )

        return user

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password

        Args:
            password (str): The password to verify
            hashed_password (str): The hashed password

        Returns:
            bool: True if the password is valid, False otherwise
        """
        return password_hasher.verify_password(password, hashed_password)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current user from the token

    Args:
        token (HTTPAuthorizationCredentials): The token to get the current user from
        db (Session): The database session

    Returns:
        User: The current user
    """
    logging.info(f"Getting current user with token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
       
        payload = await token_encoder.decode_token(token)
        username = payload.get("sub")
        token_type = payload.get("type")
        if username is None or token_type != TokenTypes.ACCESS:
            raise credentials_exception
    except JWTError:
        logging.error(f"AuthService: JWTError: {JWTError}")
        raise credentials_exception

    logging.info(f"AuthService: Username: {username}")
    user_repository = UserRepository(db)
    user = await cache(
        user_repository.get_by_username,
        key=RedisKey.AUTH_USER.format(username=username),
        args=[username],
    )

    if user is None:
        logging.error(f"User not found: {username}")
        raise credentials_exception

    logging.info(f"AuthService: User authenticated: {user.username}")
    return user


def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current admin user

    Args:
        current_user (User): The current user

    Returns:
        User: The current admin user
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user


auth_service = AuthService()
