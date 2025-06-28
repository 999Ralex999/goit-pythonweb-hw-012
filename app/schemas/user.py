from pydantic import BaseModel, Field, EmailStr

from app.enum.user_role import UserRole


class UserResponse(BaseModel):
    """
    User response model
    """

    id: int
    username: str
    email: EmailStr
    avatar: str | None
    role: UserRole


class UserModel(BaseModel):
    """
    User model
    """

    username: str | None = Field(min_length=3, max_length=255, default=None)
    email: EmailStr | None = Field(min_length=1, max_length=255, default=None)
    password: str | None = Field(min_length=8, max_length=255, default=None)
    avatar: str | None = Field(default=None)
    email_verified: bool | None = Field(default=None)
    refresh_token: str | None = Field(default=None)
    password_reset_token: str | None = Field(default=None)
    role: UserRole = Field(default=UserRole.USER)


class UserCreateRequest(BaseModel):
    """
    User create request model
    """

    username: str = Field(min_length=3, max_length=255)
    email: EmailStr = Field(min_length=1, max_length=255)
    password: str = Field(min_length=8, max_length=255)
    role: UserRole = Field(default=UserRole.USER)


class UserResendVerificationEmailRequest(BaseModel):
    """
    User resend verification email request model
    """

    email: EmailStr = Field(min_length=1, max_length=255)


class UserPasswordRestoreRequest(BaseModel):
    """
    User password restore request model
    """

    email: EmailStr = Field(min_length=1, max_length=255)


class UserPasswordUpdateRequest(BaseModel):
    """
    User password update request model
    """

    password: str = Field(min_length=8, max_length=255)
    password_reset_token: str = Field(min_length=1, max_length=255)
