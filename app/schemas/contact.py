from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr, model_validator


class ContactResponse(BaseModel):
    """
    Contact response model
    """

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str
    birthday: datetime | None
    birthday_of_the_year: int | None
    additional_info: str | None
    created_at: datetime
    updated_at: datetime


class ContactQuery(BaseModel):
    """
    Contact query model
    """

    limit: int = Field(
        default=10, ge=1, le=100, description="Limit the number of contacts to return"
    )
    offset: int = Field(
        default=0, ge=0, description="Offset the number of contacts to return"
    )
    search: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
        description="Search by first name, last name, email",
    )
    first_name: str | None = Field(
        default=None, min_length=1, max_length=255, description="Search by first name"
    )
    last_name: str | None = Field(
        default=None, min_length=1, max_length=255, description="Search by last name"
    )
    email: EmailStr | None = Field(
        default=None, min_length=1, max_length=255, description="Search by email"
    )
    phone: str | None = Field(
        default=None, min_length=1, max_length=255, description="Search by phone"
    )
    birthday_from: datetime | None = Field(
        default=None, gt=datetime(1900, 1, 1), description="Search by birthday from"
    )
    birthday_to: datetime | None = Field(
        default=None, description="Search by birthday to"
    )
    birthday_of_the_year_from: int | None = Field(
        default=None, ge=1, le=365, description="Search by birthday of the year from"
    )
    birthday_of_the_year_to: int | None = Field(
        default=None, ge=1, le=365, description="Search by birthday of the year to"
    )
    birthday_in_next_days: int | None = Field(
        default=None, ge=1, le=365, description="Search by birthday in the next days"
    )


class ContactModel(BaseModel):
    """
    Contact create model
    """

    first_name: str = Field(
        default="", min_length=1, max_length=255, description="First name"
    )
    last_name: str = Field(
        default="", min_length=1, max_length=255, description="Last name"
    )
    email: EmailStr = Field(
        default="", min_length=1, max_length=255, description="Email"
    )
    phone: str = Field(default="", min_length=0, max_length=255, description="Phone")
    birthday: datetime = Field(default=datetime.now(), description="Birthday")
    additional_info: str | None = Field(
        default=None, min_length=1, max_length=255, description="Additional info"
    )


class ContactCreateRequest(BaseModel):
    first_name: str = Field(
        default="", min_length=1, max_length=255, description="First name"
    )
    last_name: str = Field(
        default="", min_length=1, max_length=255, description="Last name"
    )
    email: EmailStr = Field(min_length=1, max_length=255, description="Email")
    phone: str = Field(default="", min_length=1, max_length=255, description="Phone")
    birthday: datetime = Field(default=datetime.now(), description="Birthday")
    additional_info: str | None = Field(
        default=None, min_length=1, max_length=255, description="Additional info"
    )
