from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import List


class Prompt(BaseModel):
    userId: str = Field(..., description="Unique ID of the user")
    prompts: List[str] = Field(
        ..., description="List of all generated prompts from a user's conversations"
    )
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Prompt creation date",
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Prompt update date",
    )


class PromptMessages(BaseModel):
    prompts: List[str] = Field(
        ...,
        description="List of four prompt messages generated from a user's conversation title, "
        "each having a maximum of 15 words",
    )
