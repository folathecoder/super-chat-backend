from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, timezone


class BaseUser(BaseModel):
    firstName: str = Field(..., description="First name of the user")
    lastName: str = Field(..., description="Last name of the user")
    email: str = Field(..., description="Email address of the user")
    occupation: Optional[str] = Field(
        None, description="The user's current occupation or job title"
    )
    industry: Optional[str] = Field(
        None, description="The industry or field the user works in"
    )
    interests: Optional[List[str]] = Field(
        None, description="List of the user's interests or hobbies"
    )
    goals: Optional[List[str]] = Field(
        None, description="Personal or professional goals the user wants to achieve"
    )
    expertiseAreas: Optional[List[str]] = Field(
        None, description="Topics or areas where the user has expertise"
    )


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
    email: Optional[str] = Field(None, description="Email address of the user")
    occupation: Optional[str] = Field(
        None, description="The user's current occupation or job title"
    )
    industry: Optional[str] = Field(
        None, description="The industry or field the user works in"
    )
    interests: Optional[List[str]] = Field(
        None, description="List of the user's interests or hobbies"
    )
    goals: Optional[List[str]] = Field(
        None, description="Personal or professional goals the user wants to achieve"
    )
    expertiseAreas: Optional[List[str]] = Field(
        None, description="Topics or areas where the user has expertise"
    )
