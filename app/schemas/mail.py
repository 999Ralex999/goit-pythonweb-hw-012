from pydantic import BaseModel, EmailStr, Field


class MailModel(BaseModel):
    """
    Mail model
    """

    to: list[EmailStr] = Field(..., description="The email address of the recipient")
    subject: str = Field(..., description="The subject of the email")
    data: dict = Field(..., description="The data of the email")
    template: str = Field(..., description="The template of the email")
