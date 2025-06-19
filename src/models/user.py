from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone


class BaseUser(BaseModel):
    firstName: str = Field(..., description="First name of the user")
    lastName: str = Field(..., description="Last name of the user")
    email: str = Field(..., description="")


class User(BaseUser):
    id: str = Field(..., description="Unique ID of the user")
    createdAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="User creation date",
    )
    updatedAt: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="User update date",
    )


class UpdateUser(BaseModel):
    firstName: Optional[str] = Field(None, description="First name of the user")
    lastName: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(None, description="")
