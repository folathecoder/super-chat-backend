from fastapi import HTTPException
from starlette import status
from src.models.conversation import (
    Conversation,
    ConversationWithMessages,
    UpdateConversation,
)
from src.schema.conversation_schema import conversation_schema
from src.db.collections import conversations_collection
from datetime import datetime, timezone
from src.utils.converters.convert_to_object_id import convert_to_object_id
from src.services.user_service import get_current_user
from src.services.message_service import get_messages, delete_messages
from typing import List


async def create_conversation() -> Conversation:
    user = await get_current_user()
    now = datetime.now(timezone.utc)

    new_conversation = {
        "userId": convert_to_object_id(user["id"]),
        "title": "New chat",
        "hasGeneratedTitle": False,
        "createdAt": now,
        "updatedAt": now,
    }

    response = await conversations_collection.insert_one(new_conversation)
    new_conversation["_id"] = response.inserted_id

    return conversation_schema(new_conversation)


async def get_conversation(conversation_id: str) -> Conversation:
    conversation = await conversations_collection.find_one(
        {"_id": convert_to_object_id(conversation_id)}
    )
    conversation_obj = conversation_schema(conversation)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with conversationId: {conversation_id} not found",
        )

    user = await get_current_user()
    user_id = user["id"]

    if conversation_obj["userId"] != user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"User with userId: {user_id} does not have access to conversation with conversationId: {conversation_id}",
        )

    return conversation_obj


async def get_conversation_with_messages(
    conversation_id: str,
) -> ConversationWithMessages:
    conversation = await get_conversation(conversation_id)
    messages = await get_messages(conversation_id)

    conversation["messages"] = messages

    return conversation


async def get_all_conversations() -> List[Conversation]:
    user = await get_current_user()

    cursor = conversations_collection.find({"userId": convert_to_object_id(user["id"])})

    all_conversations = []

    async for conversation in cursor:
        all_conversations.append(conversation_schema(conversation))

    return all_conversations


async def delete_conversation(conversation_id: str) -> None:
    conversation = await get_conversation(conversation_id)

    await delete_messages(conversation_id)

    response = await conversations_collection.delete_one(
        {"_id": convert_to_object_id(conversation["id"])}
    )

    if response.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to delete conversation with id: {conversation_id}",
        )


async def update_conversation(
    conversation_id: str, update_conversation: UpdateConversation
) -> Conversation:
    conversation = await get_conversation(conversation_id)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation with conversation_id: {conversation_id} not found",
        )

    update_conversation_obj = update_conversation.model_dump(exclude_unset=True)
    update_conversation_obj["updatedAt"] = datetime.now(timezone.utc)

    await conversations_collection.update_one(
        {"_id": convert_to_object_id(conversation_id)},
        {"$set": update_conversation_obj},
    )

    updated_conversation = await get_conversation(conversation_id)

    return updated_conversation
