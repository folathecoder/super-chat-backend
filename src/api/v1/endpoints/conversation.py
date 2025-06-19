from fastapi import APIRouter, HTTPException
from starlette import status
from src.models.conversation import Conversation
from src.services.conversation_service import (
    create_conversation,
    get_conversation,
    delete_conversation,
)

conversation_router = APIRouter()


@conversation_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=Conversation
)
async def start_conversation_endpoint():
    try:
        return await create_conversation()
    except Exception as e:
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start new conversation: {str(e)}",
        )


@conversation_router.get(
    "/{conversation_id}", status_code=status.HTTP_200_OK, response_model=Conversation
)
async def get_conversation_endpoint(conversation_id: str):
    try:
        return await get_conversation(conversation_id)
    except Exception as e:
        HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to get conversation: {str(e)}",
        )


@conversation_router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_conversation_endpoint(conversation_id: str):
    try:
        return await delete_conversation(conversation_id)
    except Exception as e:
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete conversation: {str(e)}",
        )
