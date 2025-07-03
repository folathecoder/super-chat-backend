from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from starlette import status
from typing import List, Optional
from src.models.message import Message, CreateMessage, Author
from src.models.file import FileData
from src.services.message_service import create_message
from src.services.chat_service import get_chat_response
from src.models.status import Status
from src.utils.constants.file_type import ALLOWED_FILE_TYPES
from src.core.logger import logger
from src.services.file_service import read_files_into_memory

messages_router = APIRouter()


@messages_router.post(
    "/{conversation_id}", status_code=status.HTTP_201_CREATED, response_model=Message
)
async def create_message_endpoint(
    conversation_id: str,
    background_tasks: BackgroundTasks,
    content: str = Form(...),
    author: Author = Form(...),
    status: Optional[Status] = Form(None),
    files: Optional[List[UploadFile]] = File(default=None),
):
    try:
        message = CreateMessage(content=content, author=author, status=status)
        user_message = await create_message(conversation_id, message, Author.USER)

        ai_message = CreateMessage(author=Author.AI, content="", status=Status.LOADING)
        saved_ai_message = await create_message(conversation_id, ai_message, Author.AI)

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create message: {str(e)}",
        )
