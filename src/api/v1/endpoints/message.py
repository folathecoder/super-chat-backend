from fastapi import APIRouter, HTTPException
from starlette import status
from src.models.message import Message, CreateMessage
from src.services.message_service import create_message

messages_router = APIRouter()


@messages_router.post(
    "/{conversation_id}", status_code=status.HTTP_201_CREATED, response_model=Message
)
async def create_message_endpoint(conversation_id: str, message: CreateMessage):
    try:
        return await create_message(conversation_id, message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create message: {str(e)}",
        )
