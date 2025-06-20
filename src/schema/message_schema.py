from src.models.message import Message


def message_schema(message: Message):
    return {
        "id": str(message["_id"]),
        "conversationId": str(message["conversationId"]),
        "timestamp": message["timestamp"],
        "author": message["author"],
        "content": message["content"],
    }
