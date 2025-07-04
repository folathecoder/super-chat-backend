from fastapi import APIRouter, HTTPException, BackgroundTasks
from starlette import status
from src.models.conversation import Conversation, ConversationWithMessages
from typing import List
from src.services.conversation_service import (
    create_conversation,
    delete_conversation,
    get_all_conversations,
    get_conversation_with_messages,
)

conversation_router = APIRouter()


@conversation_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=Conversation
)
async def start_conversation_endpoint():
    """
    Start a new conversation.

    Returns:
        Conversation: The newly created conversation.

    Raises:
        HTTPException: 400 Bad Request if creation fails.
    """
    try:
        return await create_conversation()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to start new conversation: {str(e)}",
        )


@conversation_router.get(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
    response_model=ConversationWithMessages,
)
async def get_conversation_endpoint(conversation_id: str):
    """
    Retrieve a conversation and its messages by ID.

    Args:
        conversation_id (str): Conversation identifier.

    Returns:
        ConversationWithMessages: Conversation data including messages.

    Raises:
        HTTPException: 404 Not Found if conversation is missing or error occurs.
    """
    try:
        return await get_conversation_with_messages(conversation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to get conversation with messages: {str(e)}",
        )


@conversation_router.get(
    "/", status_code=status.HTTP_200_OK, response_model=List[Conversation]
)
async def get_all_conversations_endpoint():
    """
    Retrieve all conversations.

    Returns:
        List[Conversation]: List of all conversations.

    Raises:
        HTTPException: 404 Not Found if retrieval fails.
    """
    try:
        return await get_all_conversations()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Failed to get conversations: {str(e)}",
        )


@conversation_router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_model=None,
)
async def delete_conversation_endpoint(
    conversation_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Delete a conversation by ID.

    Args:
        conversation_id (str): Conversation identifier.

    Raises:
        HTTPException: 400 Bad Request if deletion fails.
    """
    try:
        background_tasks.add_task(delete_conversation, conversation_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete conversation: {str(e)}",
        )
