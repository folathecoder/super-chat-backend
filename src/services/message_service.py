from fastapi import HTTPException
from starlette import status
from datetime import datetime, timezone
from typing import List
from src.models.message import Message, CreateMessage, UpdateMessage, Author
from src.db.collections import messages_collection
from src.utils.converters.convert_to_object_id import convert_to_object_id
from src.schema.message_schema import message_schema
from src.models.status import Status
from src.core.logger import logger


async def create_message(
    conversation_id: str, message: CreateMessage, author: Author
) -> Message:
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
        **message.model_dump(),
    }

    if author == Author.USER:
        new_message["status"] = Status.SUCCESS

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


async def get_message(message_id: str) -> List[Message]:
    message = await messages_collection.find_one(
        {"_id": convert_to_object_id(message_id)}
    )

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Message with messageId: {message_id} not found",
        )

    return message_schema(message)


async def update_message(message_id: str, update_data: UpdateMessage) -> Message:
    await messages_collection.update_one(
        {"_id": convert_to_object_id(message_id)},
        {"$set": update_data.model_dump(exclude_unset=True)},
    )

    message = await get_message(message_id)

    return message


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
