import logging
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta, timezone
from app.errors.token import TokenDecodeException, TokenExpiredException
from app.core.config import settings

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)

# Типи токенів для системи аутентифікації
class TokenTypes:
    ACCESS = "access"
    REFRESH = "refresh"

class TokenEncoder:
    """
    Клас для створення та декодування JWT-токенів.
    """

    def __init__(self, secret_key: str, algorithm: str, default_expires_delta: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.default_expires_delta = default_expires_delta

    async def create_token(self, data: dict, expires_delta: Optional[int] = None):
        """
        Створити JWT-токен.
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(timezone.utc) + timedelta(seconds=self.default_expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def decode_token(self, token: str) -> dict:
        """
        Декодувати та перевірити JWT-токен.
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if not payload:
                raise TokenDecodeException("Token is invalid")
            if payload.get("exp") < datetime.now(timezone.utc).timestamp():
                raise TokenExpiredException("Token has expired")
            logging.info(f"Token decoded successfully: {payload}")
            return payload
        except jwt.JWTError as e:
            logging.error(f"Token is invalid: {e}")
            raise TokenDecodeException("Token is invalid")


token_encoder = TokenEncoder(
    secret_key=settings.JWT_SECRET,
    algorithm=settings.JWT_ALGORITHM,
    default_expires_delta=settings.JWT_EXPIRATION_SECONDS,
)

