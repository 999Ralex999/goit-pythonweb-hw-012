from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    # === DOMAIN ===
    DOMAIN: str  # e.g., http://127.0.0.1:8000

    # === DATABASE ===
    DB_URL: str  # Async URL for SQLAlchemy (PostgreSQL)
    DB_SYNC_URL: str  # ⬅️ Синхронный URL для Alembic

    # === MAIL ===
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_PORT: int
    MAIL_SERVER: str
    MAIL_FROM_NAME: str
    MAIL_STARTTLS: bool
    MAIL_SSL_TLS: bool
    USE_CREDENTIALS: bool
    VALIDATE_CERTS: bool

    # === JWT ===
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_SECONDS: int  # lifetime of access token
    JWT_REFRESH_EXPIRATION_SECONDS: int  # lifetime of refresh token

    # === CLOUDINARY ===
    CLOUDINARY_NAME: str
    CLOUDINARY_API_KEY: str
    CLOUDINARY_API_SECRET: str

    model_config = ConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()



