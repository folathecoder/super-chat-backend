from pydantic import BaseModel, Field


class Newsletter(BaseModel):
    headline: str = Field(..., description="The title of the newsletter")
    body: str = Field(..., description="The main content of the newsletter")


class CreateNewsletter(BaseModel):
    firstName: str = Field(..., description="User's first name")
    occupation: str = Field(
        ..., description="User's job title or role (e.g. Software Engineer)"
    )
    tone: str = Field(
        ...,
        description="Preferred tone of the newsletter (e.g. casual, professional, witty)",
    )
    categories: str = Field(
        ...,
        description="Topics or categories the user is interested in (e.g. AI, Finance, Health)",
    )
    reason: str = Field(
        ...,
        description="Why the user wants to receive this newsletter (e.g. to stay updated, for research, etc.)",
    )
