from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime


class Base(DeclarativeBase):
    """
    Base class for all models
    """

    pass


class CreatedAtTimestamp:
    """
    Abstract class for created at timestamp
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now
    )


class UpdatedAtTimestamp:
    """
    Abstract class for updated at timestamp
    """

    __abstract__ = True

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.now, onupdate=datetime.now
    )


class AllTimestamps(CreatedAtTimestamp, UpdatedAtTimestamp):
    """
    Abstract class for all timestamps
    """

    __abstract__ = True
