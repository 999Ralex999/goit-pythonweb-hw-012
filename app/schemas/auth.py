from pydantic import BaseModel, Field, EmailStr


class AuthResponse(BaseModel):
    """
    Auth response model
    """

    access_token: str | None = Field(
        default=None, description="Access token used to authenticate requests"
    )
    refresh_token: str | None = Field(
        default=None, description="Refresh token used to refresh access token"
    )
    token_type: str = Field(default="bearer", description="Token type")


class TokenRefreshRequest(BaseModel):
    """
    Refresh token request model
    """

    refresh_token: str = Field(
        default="", min_length=1, max_length=255, description="Refresh token"
    )
