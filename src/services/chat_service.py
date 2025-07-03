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


async def get_chat_response(
    conversation_id: str,
    message_id: str,
    message: CreateMessage,
    file_data_list: List[FileData],
) -> Message:
    try:
        user_message = message.model_dump()
        query = user_message["content"]

        question = await retrieval_service.run(
            query=query,
            conversation_id=conversation_id,
            message_id=message_id,
            files=file_data_list,
        )

        print("question", question)

        input_messages = [HumanMessage(content=query)]
        config = get_thread_config(conversation_id)

        output = await app.ainvoke({"messages": input_messages}, config=config)
        response_text = output["messages"][-1].content

        if not response_text:
            await get_chat_response_failed(message_id)
            raise ValueError("Empty response received from the model.")

        update_data = UpdateMessage(content=response_text, status=Status.SUCCESS)
        updated_ai_message = await update_message(message_id, update_data)

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
    update_data = UpdateMessage(status=Status.FAILED)
    await update_message(message_id, update_data)


async def get_chat_title(conversation_id: str) -> None:
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

            await update_conversation(conversation_id, update_conversation_data)

    except Exception as e:
        raise RuntimeError(f"Failed to get chat title: {str(e)}")
