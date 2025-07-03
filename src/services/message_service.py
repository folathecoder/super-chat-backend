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
    """
    Create a new message in a conversation.

    Args:
        conversation_id (str): ID of the conversation.
        message (CreateMessage): Message data to create.
        author (Author): Author type (USER or AI).

    Returns:
        Message: Created message object.

    Raises:
        HTTPException: If conversation does not exist.
    """
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

    # Set status to SUCCESS immediately for user messages
    if author == Author.USER:
        new_message["status"] = Status.SUCCESS

    response = await messages_collection.insert_one(new_message)
    new_message["_id"] = response.inserted_id

    return message_schema(new_message)


async def get_messages(conversation_id: str) -> List[Message]:
    """
    Retrieve all messages for a conversation sorted by timestamp.

    Args:
        conversation_id (str): Conversation ID.

    Returns:
        List[Message]: List of messages.
    """
    messages = (
        await messages_collection.find(
            {"conversationId": convert_to_object_id(conversation_id)}
        )
        .sort("timestamp", 1)
        .to_list(length=None)
    )

    return [message_schema(msg) for msg in messages]


async def get_message(message_id: str) -> Message:
    """
    Retrieve a single message by its ID.

    Args:
        message_id (str): Message ID.

    Returns:
        Message: Message object.

    Raises:
        HTTPException: If message is not found.
    """
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
    """
    Update a message with new data.

    Args:
        message_id (str): ID of the message to update.
        update_data (UpdateMessage): Data for update.

    Returns:
        Message: Updated message object.
    """
    await messages_collection.update_one(
        {"_id": convert_to_object_id(message_id)},
        {"$set": update_data.model_dump(exclude_unset=True)},
    )

    message = await get_message(message_id)
    return message


async def delete_messages(conversation_id: str) -> None:
    """
    Delete all messages belonging to a conversation.

    Args:
        conversation_id (str): Conversation ID.

    Raises:
        HTTPException: If conversation does not exist.
    """
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
