from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class MessageCreate(BaseModel):
    """Schema for creating a message in a course chat."""
    content: str = Field(..., description="Message content")
    course_id: int = Field(..., description="ID of the course")


class MessageRead(BaseModel):
    """Schema for reading a message."""
    id: int = Field(..., description="Unique identifier for the message")
    content: str = Field(..., description="Message content")
    course_id: int = Field(..., description="ID of the course")
    sender_id: int = Field(..., description="ID of the sender")
    created_at: datetime = Field(..., description="Timestamp of when the message was sent")

    model_config = ConfigDict(from_attributes=True)
