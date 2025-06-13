from datetime import datetime
from pydantic import BaseModel, Field, EmailStr

class ContactModel(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=255, description="First name")
    last_name: str = Field(..., min_length=1, max_length=255, description="Last name")
    email: EmailStr = Field(..., max_length=255, description="Email")
    phone: str = Field(..., min_length=1, max_length=255, description="Phone")
    birthday: datetime = Field(default_factory=datetime.now, description="Birthday")
    additional_info: str | None = Field(default=None, max_length=255, description="Additional info")

class ContactResponse(ContactModel):
    id: int
    birthday_of_the_year: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ContactQuery(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    search: str | None = Field(default=None, max_length=255)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None)
    phone: str | None = Field(default=None, max_length=255)
    birthday_from: datetime | None = Field(default=None)
    birthday_to: datetime | None = Field(default=None)
    birthday_of_the_year_from: int | None = Field(default=None, ge=1, le=365)
    birthday_of_the_year_to: int | None = Field(default=None, ge=1, le=365)
    birthday_in_next_days: int | None = Field(default=None, ge=1, le=365)


