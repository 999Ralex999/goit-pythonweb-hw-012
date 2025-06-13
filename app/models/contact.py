from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING
from app.models.base import Base, TimestampsMixin

if TYPE_CHECKING:
    from app.models.user import User

class Contact(Base, TimestampsMixin):
    """
    Модель контактної особи, пов'язаної з користувачем.
    """
    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="contacts")

    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    birthday: Mapped[datetime | None] = mapped_column(Date, nullable=True)
    additional_info: Mapped[str | None] = mapped_column(String, nullable=True)
    birthday_of_the_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
