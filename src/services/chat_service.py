from src.llm.memories.chat_memory import app
from src.models.message import Message, CreateMessage, UpdateMessage
from src.models.status import Status
from langchain_core.messages import HumanMessage
from src.services.message_service import update_message


async def get_chat_response(
    conversation_id: str, message_id: str, message: CreateMessage
) -> Message:
    try:
        user_message = message.model_dump()
        input_messages = [HumanMessage(content=user_message["content"])]
        config = {"configurable": {"thread_id": conversation_id}}

        output = await app.ainvoke({"messages": input_messages}, config=config)
        response_text = output["messages"][-1].content

        if not response_text:
            await get_chat_response_failed(message_id)
            raise ValueError("Empty response received from the model.")

        update_data = UpdateMessage(content=response_text, status=Status.SUCCESS)
        updated_ai_message = await update_message(message_id, update_data)

        return updated_ai_message

    except Exception as e:
        await get_chat_response_failed(message_id)
        raise RuntimeError(f"Failed to get chat response: {str(e)}")


async def get_chat_response_failed(message_id: str) -> None:
    update_data = UpdateMessage(status=Status.FAILED)
    await update_message(message_id, update_data)
