from pydantic import BaseModel, Field
from typing import Optional


class BaseUser(BaseModel):
    firstName: str = Field(..., description="First name of the user")
    lastName: str = Field(..., description="Last name of the user")
    email: str = Field(..., description="")


class User(BaseUser):
    id: str = Field(..., description="Unique ID of the user")


class UpdateUser(BaseModel):
    firstName: Optional[str] = Field(None, description="First name of the user")
    lastName: Optional[str] = Field(None, description="Last name of the user")
    email: Optional[str] = Field(None, description="")
