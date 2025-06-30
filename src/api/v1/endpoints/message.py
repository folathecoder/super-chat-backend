from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Form
from starlette import status
from typing import List, Optional
from src.models.message import Message, CreateMessage, Author
from src.services.message_service import create_message
from src.services.chat_service import get_chat_response
from src.models.status import Status
from src.services.loader_service import loader_service

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

        background_tasks.add_task(
            get_chat_response, conversation_id, saved_ai_message["id"], message
        )

        await loader_service.run(files)

        print("files", files)

        return user_message
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create message: {str(e)}",
        )
