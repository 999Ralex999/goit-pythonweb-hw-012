from pydantic import BaseModel, Field, EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    avatar: str | None = None

    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=255)
    avatar: str | None = Field(default=None)
    email_verified: bool | None = Field(default=None)
    refresh_token: str | None = Field(default=None)

class UserCreateRequest(BaseModel):
    username: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=255)

class UserResendVerificationEmailRequest(BaseModel):
    email: EmailStr = Field(min_length=1, max_length=255)

