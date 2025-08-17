from typing import List, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, add_messages, START
from src.llm.models.openai_model import async_get_openai_model, model
from langgraph.checkpoint.memory import MemorySaver
from src.llm.prompts.prompts import super_chat_prompt
from src.services.user_service import user_profile_context


# Define the chat state type tracking the list of messages
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


# Initialize the state graph workflow with ChatState
workflow = StateGraph(ChatState)


# Async model node that calls OpenAI with system + chat messages and returns new message list
async def call_model(state: ChatState):
    user_context = await user_profile_context()

    messages = state["messages"]
    system_message = SystemMessage(
        content=super_chat_prompt.format(user_profile=user_context)
    )

    llm = await async_get_openai_model()
    response = await llm.ainvoke([system_message] + messages)

    return {"messages": [response]}


def get_thread_config(conversation_id: str) -> dict:
    # Returns config dict with thread ID for conversation tracking
    return {"configurable": {"thread_id": conversation_id}}


# Connect workflow nodes: start to model node
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory checkpointing to persist state
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
