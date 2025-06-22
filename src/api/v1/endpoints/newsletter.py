from fastapi import APIRouter, HTTPException
from starlette import status
from src.models.newsletter import Newsletter, CreateNewsletter
from src.services.newsletter_service import generate_newsletter

newsletter_router = APIRouter()


@newsletter_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=Newsletter
)
async def generate_newsletter_endpoint(data: CreateNewsletter):
    try:
        return await generate_newsletter(data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to generate newsletter: {str(e)}",
        )
