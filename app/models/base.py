from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime

class Base(DeclarativeBase):
    """
    Базовий клас для всіх моделей SQLAlchemy.
    """
    pass

class CreatedAtTimestamp:
    """
    Міксин для автоматичного зберігання дати створення.
    """
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

class UpdatedAtTimestamp:
    """
    Міксин для автоматичного зберігання дати оновлення.
    """
    __abstract__ = True
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )

class TimestampsMixin(CreatedAtTimestamp, UpdatedAtTimestamp):
    """
    Міксин для об'єднання created_at та updated_at.
    """
    __abstract__ = True
