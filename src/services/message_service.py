from fastapi import HTTPException
from starlette import status
from datetime import datetime, timezone
from typing import List
from src.models.message import Message, CreateMessage
from src.db.collections import messages_collection
from src.utils.converters.convert_to_object_id import convert_to_object_id
from src.schema.message_schema import message_schema
from src.core.logger import logger


async def create_message(conversation_id: str, message: CreateMessage) -> Message:
    from src.services.conversation_service import get_conversation

    conversation = await get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with conversationId: {conversation_id} not found",
        )

    new_message = {
        "conversationId": convert_to_object_id(conversation_id),
        "timestamp": datetime.now(timezone.utc),
        "status": "success",
        **message.model_dump(),
    }

    response = await messages_collection.insert_one(new_message)

    new_message["_id"] = response.inserted_id

    return message_schema(new_message)


async def get_messages(conversation_id: str) -> List[Message]:
    messages = (
        await messages_collection.find(
            {"conversationId": convert_to_object_id(conversation_id)}
        )
        .sort("timestamp", 1)
        .to_list(length=None)
    )

    return [message_schema(msg) for msg in messages]


async def delete_messages(conversation_id: str) -> None:
    from src.services.conversation_service import get_conversation

    conversation = await get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with conversationId: {conversation_id} not found",
        )

    response = await messages_collection.delete_many(
        {"conversationId": convert_to_object_id(conversation_id)}
    )

    logger.info(
        f"Successfully deleted {response.deleted_count} messages from conversation: {conversation_id}"
    )
