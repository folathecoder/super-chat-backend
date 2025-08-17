from fastapi import (
    APIRouter,
    HTTPException,
    BackgroundTasks,
    UploadFile,
    File,
    Form,
    status as http_status,
)
from typing import List, Optional
from src.models.message import Message, CreateMessage, Author
from src.services.message_service import create_message
from src.services.chat_service import get_chat_response
from src.models.status import Status
from src.services.file_service import read_files_into_memory
from src.core.server.socket_server import sio
from src.core.events import SOCKET_EVENTS
from src.utils.converters.socketio_utils import (
    async_safe_socket_emit,
)

messages_router = APIRouter()


@messages_router.post(
    "/{conversation_id}",
    status_code=http_status.HTTP_201_CREATED,
    response_model=Message,
)
async def create_message_endpoint(
    conversation_id: str,
    background_tasks: BackgroundTasks,
    content: str = Form(...),
    author: Author = Form(...),
    files: Optional[List[UploadFile]] = File(default=None),
):
    """
    Create a user message and trigger async AI response generation.

    Args:
        conversation_id (str): Conversation ID.
        background_tasks (BackgroundTasks): For running async tasks.
        content (str): Message text content.
        author (Author): Message author.
        files (Optional[List[UploadFile]]): Optional uploaded files.

    Returns:
        Message: Created user message.

    Raises:
        HTTPException: 400 Bad Request on failure.
    """
    try:
        # Create the user message
        message = CreateMessage(content=content, author=author, status=Status.SUCCESS)
        user_message = await create_message(conversation_id, message, Author.USER)

        # Emit user message creation event with safe serialization
        await async_safe_socket_emit(
            sio,
            SOCKET_EVENTS["CHAT_USER_CREATE"],
            user_message,
            room=conversation_id,
        )

        # Create AI message placeholder
        ai_message = CreateMessage(author=Author.AI, content="", status=Status.LOADING)
        saved_ai_message = await create_message(conversation_id, ai_message, Author.AI)

        # Emit AI response (loading state)
        await async_safe_socket_emit(
            sio,
            SOCKET_EVENTS["CHAT_AI_MESSAGE"],
            saved_ai_message,
            room=conversation_id,
        )

        # Process uploaded files
        file_data_list = await read_files_into_memory(files)

        background_tasks.add_task(
            get_chat_response,
            conversation_id,
            saved_ai_message["id"],
            message,
            file_data_list,
        )

        return user_message

    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create message: {str(e)}",
        )
