from pydantic import BaseModel, EmailStr, Field

class MailModel(BaseModel):
    to: list[EmailStr] = Field(..., description="Recipient email addresses")
    subject: str = Field(..., description="Subject of the email")
    data: dict = Field(..., description="Data passed to template")
    template: str = Field(..., description="Template filename")

