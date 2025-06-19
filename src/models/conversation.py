from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class BaseConversation(BaseModel):
    userId: str = Field(..., description="Unique ID of the user")
    title: str = Field(..., description="Title of the conversation")


class Conversation(BaseConversation):
    id: str = Field(..., description="Conversation ID")
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Conversation creation date",
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Conversation update date",
    )


class UpdateConversation(BaseModel):
    title: Optional[str] = Field(None, description="New title of the conversation")
