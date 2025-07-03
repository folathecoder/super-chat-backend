from src.models.conversation import Conversation


def conversation_schema(conversation: Conversation):
    return {
        "id": str(conversation["_id"]),
        "userId": str(conversation["userId"]),
        "title": conversation["title"],
        "hasGeneratedTitle": conversation["hasGeneratedTitle"],
        "hasFilesUploaded": conversation["hasFilesUploaded"],
        "createdAt": conversation["createdAt"],
        "updatedAt": conversation["updatedAt"],
    }
