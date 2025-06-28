from sqlalchemy import Boolean, Integer, String, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING
from app.entity.base import AllTimestamps, Base
from app.enum.user_role import UserRole

if TYPE_CHECKING:
    from app.entity.contact import Contact


class User(Base, AllTimestamps):
    """
    User model
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String, nullable=False)
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    refresh_token: Mapped[str] = mapped_column(String, nullable=True)
    password_reset_token: Mapped[str] = mapped_column(String, nullable=True)
    avatar: Mapped[str] = mapped_column(String, nullable=True)
    contacts: Mapped[list["Contact"]] = relationship(back_populates="user")
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
        default=UserRole.USER,
    )
