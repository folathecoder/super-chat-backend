from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum


class Author(str, Enum):
    USER = "user"
    AI = "ai"


class BaseMessage(BaseModel):
    conversationId: str = Field(..., description="Unique ID of the conversation")
    content: str = Field(
        ..., description="Content of the message e.g text, image, etc."
    )
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation date",
    )
    author: Author = Field(..., description="Author of the conversation")


class Message(BaseMessage):
    id: str = Field(..., description="Unique ID of the message")


class CreateMessage(BaseModel):
    author: Author = Field(..., description="Author of the conversation")
    content: str = Field(
        ..., description="Content of the message e.g text, image, etc."
    )
