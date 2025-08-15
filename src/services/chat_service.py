import asyncio
from fastapi import HTTPException
from typing import List
from starlette import status
from src.llm.memories.chat_memory import app, get_thread_config
from src.models.message import Message, CreateMessage, UpdateMessage
from src.models.status import Status
from langchain_core.messages import HumanMessage
from src.services.message_service import update_message
from src.services.conversation_service import update_conversation, get_conversation
from src.models.conversation import UpdateConversation
from src.models.file import FileData
from src.core.logger import logging
from src.services.retrieval_service import retrieval_service
from src.llm.prompts import super_chat_conversation_title_prompt
from src.core.server.socket_server import sio
from src.core.events import SOCKET_EVENTS
from src.utils.converters.socketio_utils import (
    async_safe_socket_emit,
)


async def get_chat_response(
    conversation_id: str,
    message_id: str,
    message: CreateMessage,
    file_data_list: List[FileData],
) -> Message:
    """
    Handle user message by retrieving context, invoking chat model, and updating AI response.

    Args:
        conversation_id (str): ID of the conversation.
        message_id (str): ID of the user message.
        message (CreateMessage): The user message data.
        file_data_list (List[FileData]): List of files uploaded by user.

    Returns:
        Message: Updated AI message with generated content.

    Raises:
        RuntimeError: If the chat response generation fails.
    """
    try:
        user_message = message.model_dump()
        query = user_message["content"]

        # Retrieve relevant context using retrieval service
        query_with_context = await retrieval_service.run(
            query=query,
            conversation_id=conversation_id,
            message_id=message_id,
            files=file_data_list,
        )

        input_messages = [HumanMessage(content=query_with_context)]
        config = get_thread_config(conversation_id)

        # Invoke the chat model asynchronously with context
        output = await app.ainvoke({"messages": input_messages}, config=config)
        response_text = output["messages"][-1].content

        if not response_text:
            await get_chat_response_failed(message_id)
            raise ValueError("Empty response received from the model.")

        # Update AI message with generated response and success status
        update_data = UpdateMessage(content=response_text, status=Status.SUCCESS)
        updated_ai_message = await update_message(message_id, update_data)

        # Launch background task to generate conversation title asynchronously
        title_task = asyncio.create_task(
            get_chat_title(conversation_id), name="generate_chat_title"
        )

        title_task.add_done_callback(
            lambda t: logging.info(
                f"Title generation completed for conversation_id={conversation_id}"
            )
        )

        return updated_ai_message

    except Exception as e:
        await get_chat_response_failed(message_id)
        raise RuntimeError(f"Failed to get chat response: {str(e)}")


async def get_chat_response_failed(message_id: str) -> None:
    """
    Mark a chat response message as failed.

    Args:
        message_id (str): ID of the message to update.
    """
    update_data = UpdateMessage(status=Status.FAILED)
    await update_message(message_id, update_data)


async def get_chat_title(conversation_id: str) -> None:
    """
    Generate and update conversation title using chat model if not already generated.

    Args:
        conversation_id (str): ID of the conversation.

    Raises:
        RuntimeError: If title generation fails.
    """
    try:
        conversation = await get_conversation(conversation_id)

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with conversationId: {conversation_id} not found",
            )

        if conversation["hasGeneratedTitle"] == False:
            config = get_thread_config(conversation_id)

            input_messages = [
                HumanMessage(content=super_chat_conversation_title_prompt.format())
            ]

            output = await app.ainvoke({"messages": input_messages}, config=config)
            response_text = output["messages"][-1].content

            if not response_text:
                raise ValueError("Empty response received from the model.")

            update_conversation_data = UpdateConversation(
                title=response_text, hasGeneratedTitle=True
            )

            updated_conversation = await update_conversation(
                conversation_id, update_conversation_data
            )

            await async_safe_socket_emit(
                sio,
                SOCKET_EVENTS["CHAT_TITLE_CREATE"],
                updated_conversation,
                room=conversation_id,
            )

    except Exception as e:
        raise RuntimeError(f"Failed to get chat title: {str(e)}")
