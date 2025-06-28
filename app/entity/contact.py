from datetime import datetime
from sqlalchemy import Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship
from typing import TYPE_CHECKING

from app.entity.base import AllTimestamps, Base

if TYPE_CHECKING:
    from app.entity.user import User


class Contact(Base, AllTimestamps):
    """
    Contact model
    """

    __tablename__ = "contacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id"), nullable=False
    )
    user: Mapped["User"] = relationship(back_populates="contacts")
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    _birthday: Mapped[datetime] = mapped_column(Date, nullable=True, name="birthday")
    _birthday_of_the_year: Mapped[int] = mapped_column(
        Integer, nullable=True, name="birthday_of_the_year"
    )
    additional_info: Mapped[str] = mapped_column(String, nullable=True)

    @property
    def birthday_of_the_year(self) -> int | None:
        return self._birthday_of_the_year

    @birthday_of_the_year.setter
    def birthday_of_the_year(self, value: int | None) -> None:
        pass

    @property
    def birthday(self) -> datetime | None:
        return self._birthday

    @birthday.setter
    def birthday(self, value: datetime | None) -> None:
        self._birthday = value
        if value:
            self._birthday_of_the_year = value.timetuple().tm_yday
        else:
            self._birthday_of_the_year = None

    def __repr__(self):
        return f"Contact(id={self.id}, user_id={self.user_id}, first_name={self.first_name}, last_name={self.last_name}, email={self.email}, phone={self.phone}, birthday={self.birthday}, additional_info={self.additional_info})"
