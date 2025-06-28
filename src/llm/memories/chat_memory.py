from typing import List, Annotated
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage, SystemMessage
from langgraph.graph import StateGraph, add_messages, START
from src.llm.models.openai_model import async_get_openai_model
from langgraph.checkpoint.memory import MemorySaver
from src.llm.prompts import super_chat_prompt


# Define state that will track the message history
class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


# Create graph
workflow = StateGraph(ChatState)


# Define model node
async def call_model(state: ChatState):
    messages = state["messages"]
    system_message = SystemMessage(content=super_chat_prompt.format())

    llm = await async_get_openai_model()
    response = await llm.ainvoke([system_message] + messages)

    return {"messages": [response]}


def get_thread_config(conversation_id: str) -> dict:
    return {"configurable": {"thread_id": conversation_id}}


# Add single node
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory persistence
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
