from datetime import datetime
import json
from pydantic import BaseModel, Field
from typing import List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_core.output_parsers.openai_tools import PydanticToolsParser
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage
from langchain_tavily import TavilySearch
from langgraph.graph import END, MessageGraph

# Pydantic Classes


class Reflection(BaseModel):
    missing: str = Field(description="Critique of what is missing.")
    superfluous: str = Field(description="Critique of what is superfluous")


class AnswerQuestion(BaseModel):
    answer: str = Field(description="~250 word detailed answer to the question.")
    search_queries: List[str] = Field(
        description="1–3 search queries for researching improvements to address the critique of your current answer."
    )
    reflection: Reflection = Field(description="Your reflection on the initial answer.")


class ReviseAnswer(AnswerQuestion):
    references: List[str] = Field(description="List of citations")


responder_pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])
revisor_pydantic_parser = PydanticToolsParser(tools=[ReviseAnswer])

# Instructions

responder_instruction = "Provide a 250-word answer"

revisor_instruction = """Revise your previous answer using the new information.
    - You should use the previous critique to add important information to your answer.
    - You MUST include numerical citations in your revised answer to ensure it can be verified.
    - Add a "References" section to the bottom of your answer (which does not count towards the word limit). In form of:
        - [1] https://example.com
        - [2] https://example.com
    - You should use the previous critique to remove superfluous information from your answer and make SURE it is not more than 250 words."""

# Reusable Actor prompt template

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """You are expert AI researcher.
            Current time: {time}
            {instruction}
            2. Reflect and critique your answer. Be severe to maximize improvement.
            3. After the reflection, **list 1–3 search queries separately** for researching improvements. Do not include them inside the reflection.
            """
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "Answer the user's question above using the required format."),
    ]
).partial(
    time=lambda: datetime.now().isoformat(),
)

llm = ChatOpenAI(model="gpt-4o")

# Responder prompt template

responder_prompt_template = actor_prompt_template.partial(
    instruction=responder_instruction
)

responder_chain = responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)

# Revisor prompt template

revisor_prompt_template = actor_prompt_template.partial(instruction=revisor_instruction)

revisor_chain = revisor_prompt_template | llm.bind_tools(
    tools=[ReviseAnswer], tool_choice="ReviseAnswer"
)

# Execute Tool

tavily_search = TavilySearch(max_results=5)


def execute_tools(state: List[BaseMessage]) -> List[BaseMessage]:
    last_message: AIMessage = state[-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return []

    tool_messages = []

    for tool_call in last_message.tool_calls:
        if tool_call["name"] in ["AnswerQuestion", "ReviseAnswer"]:
            call_id = tool_call["id"]
            search_queries = tool_call["args"].get("search_queries", [])

            query_results = {}

            for query in search_queries:
                result = tavily_search.invoke(query)
                query_results[query] = result

            tool_messages.append(
                ToolMessage(content=json.dumps(query_results), tool_call_id=call_id)
            )

    return tool_messages


def event_loop(state: List[BaseMessage]) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state)
    num_iterations = count_tool_visits
    if num_iterations > 2:
        return END
    return "execute_tools"


graph = MessageGraph()

graph.set_entry_point("responder")

graph.add_node("responder", responder_chain)
graph.add_node("execute_tools", execute_tools)
graph.add_node("revisor", revisor_chain)

graph.add_edge("responder", "execute_tools")
graph.add_edge("execute_tools", "revisor")
graph.add_conditional_edges("revisor", event_loop)

app = graph.compile()

print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

response = app.invoke(
    "What is the Future of Software Engineering and how AI will affect the industry?"
)

print(response)
