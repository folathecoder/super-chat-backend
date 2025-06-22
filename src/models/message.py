from pydantic import BaseModel, Field
from datetime import datetime, timezone
from enum import Enum
from src.models.status import Status
from typing import Optional

content_description = "Content of the message e.g text, image, etc."
status_description = "Status of the message"


class Author(str, Enum):
    USER = "user"
    AI = "ai"


class Status(str, Enum):
    LOADING = "loading"
    SUCCESS = "success"
    FAILED = "failed"


class BaseMessage(BaseModel):
    conversationId: str = Field(..., description="Unique ID of the conversation")
    content: str = Field(..., description=content_description)
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Message creation date",
    )
    author: Author = Field(..., description="Author of the conversation")
    status: Optional[Status] = Field(None, description=status_description)


class Message(BaseMessage):
    id: str = Field(..., description="Unique ID of the message")


class CreateMessage(BaseModel):
    author: Author = Field(..., description="Author of the conversation")
    content: str = Field(..., description=content_description)
    status: Optional[Status] = Field(None, description=status_description)


class UpdateMessage(BaseModel):
    content: Optional[str] = Field(None, description=content_description)
    status: Optional[Status] = Field(None, description=status_description)
