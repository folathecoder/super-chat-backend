from fastapi import APIRouter, HTTPException
from starlette import status
from src.models.prompt import Prompt
from src.services.prompt_service import generate_user_prompt
from src.services.user_service import get_current_user

prompt_router = APIRouter()


@prompt_router.get("/", status_code=status.HTTP_201_CREATED, response_model=Prompt)
async def get_user_prompt():
    try:
        user_prompt = await generate_user_prompt()

        return user_prompt
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to get user prompts: {str(e)}",
        )
