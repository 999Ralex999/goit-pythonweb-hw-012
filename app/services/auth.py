import logging
from fastapi import Depends, HTTPException, status
from jose import JWTError
from fastapi.security import OAuth2PasswordBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.errors.token import TokenDecodeException
from app.security.passwords import password_hasher
from app.models.user import User
from app.security.tokens import TokenTypes, token_encoder
from app.services.user import UserService
from app.repository.user import UserRepository
from app.db.session import get_db
from app.core.config import settings

# OAuth2 dependency для FastAPI
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
    Сервіс для роботи з аутентифікацією та токенами.
    """

    async def create_access_token(self, user: User):
        """Створити access token"""
        payload = {
            "sub": user.username,
            "type": TokenTypes.ACCESS,
        }
        return await token_encoder.create_token(payload)

    async def create_refresh_token(self, user: User):
        """Створити refresh token"""
        payload = {
            "sub": user.username,
            "type": TokenTypes.REFRESH,
        }
        return await token_encoder.create_token(
            payload,
            expires_delta=settings.JWT_REFRESH_EXPIRATION_SECONDS,
        )

    async def verify_refresh_token(self, refresh_token: str, db: AsyncSession) -> User | None:
        """Перевірити refresh token"""
        payload = await token_encoder.decode_token(refresh_token)
        username = payload.get("sub")
        if payload.get("type") != TokenTypes.REFRESH or username is None:
            raise TokenDecodeException("Invalid refresh token")
        user_repository = UserRepository(db)
        user = await user_repository.get_by_username(username)
        if not user or user.refresh_token != refresh_token:
            raise TokenDecodeException("Invalid refresh token")
        return user

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        """Перевірити пароль"""
        return password_hasher.verify_password(password, hashed_password)


async def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Отримати поточного користувача з токену.
    """
    logging.info(f"Getting current user with token: {token}")
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode JWT
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
    user_service = UserService(user_repository)
    user = await user_service.get_user_by_username(username)

    if user is None:
        logging.error(f"User not found: {username}")
        raise credentials_exception

    logging.info(f"AuthService: User authenticated: {user.username}")
    return user


auth_service = AuthService()
