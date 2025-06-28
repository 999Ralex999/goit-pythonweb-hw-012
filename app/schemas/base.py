from pydantic import BaseModel, Field


class MessageResponse(BaseModel):
    """
    Response with message
    """

    message: str = Field(default="")
