import logging
from typing import Optional
from jose import jwt
from datetime import datetime, timedelta, timezone

UTC = timezone.utc  

from app.exceptions.token_decode_exception import TokenDecodeException
from app.exceptions.token_expired_exception import TokenExpiredException
from app.conf.config import settings

logging.basicConfig(
    format="%(asctime)s %(message)s",
    level=logging.INFO,
)


class TokenEncoder:
    """
    Token encoder

    Attributes:
        secret_key (str): The secret key for the token
        algorithm (str): The algorithm for the token
        default_expires_delta (int): The default expiration time for the token
    """

    def __init__(self, secret_key: str, algorithm: str, default_expires_delta: int):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.default_expires_delta = default_expires_delta

    async def create_token(self, data: dict, expires_delta: Optional[int] = None):
        """
        Create a token

        Args:
            data (dict): The data to encode
            expires_delta (Optional[int]): The expiration time for the token

        Returns:
            str: The encoded token
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
        else:
            expire = datetime.now(UTC) + timedelta(seconds=self.default_expires_delta)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def decode_token(self, token: str) -> dict:
        """
        Decode a token

        Args:
            token (str): The token to decode

        Returns:
            dict: The decoded token
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if not payload:
                raise TokenDecodeException("Token is invalid")
            if payload.get("exp") < datetime.now(UTC).timestamp():
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
