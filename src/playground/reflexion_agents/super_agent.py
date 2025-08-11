import json
from datetime import datetime
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from langchain_tavily import TavilySearch
from langgraph.graph import MessageGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, ToolMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")
tavily_search = TavilySearch(max_results=4)


# Define all prompt output structure


class Citation(BaseModel):
    tag_name: str = Field(
        ...,
        description="A short, unique identifier or label for the citation used to reference it within the text. It should be the name of the source, for example LinkedIn, Google, Wikipedia, etc.",
    )
    title: str = Field(
        ...,
        description="The full title or name of the source being cited (e.g., article title, book name).",
    )
    description: str = Field(
        ...,
        description="A brief summary or explanation of the cited source, max 250 characters.",
        max_length=150,
    )
    url: str = Field(
        ...,
        description="The direct URL or link to the source, allowing users or systems to access the original content.",
    )
    number: int = Field(
        ...,
        description="The citation number used for ordering or referencing within the document (e.g., [1], [2]).",
    )


class Responder(BaseModel):
    response: str = Field(
        ..., description="The AI-generated answer to the user's question."
    )
    reflection: str = Field(
        ...,
        description=(
            "The agent's self-assessment highlighting flaws or errors in the response, "
            "with concrete examples and suggestions for improvement."
        ),
    )
    search_queries: List[str] = Field(
        ...,
        description=(
            "List of search queries the agent intends to use to gather more details if needed. "
            "This can be empty if the question is trivial or the agent believes the question has been answered correctly."
        ),
    )
    is_trivial: bool = Field(
        ...,
        description="Indicates whether the user's question is considered trivial and does not require tool augmentation or deep reasoning. True if trivial, False otherwise.",
    )


class Grader(BaseModel):
    correctness: int = Field(
        ...,
        ge=0,
        le=10,
        description="How factually accurate is the response? Score from 1 (completely incorrect) to 10 (fully correct).",
    )
    completeness: int = Field(
        ...,
        ge=0,
        le=10,
        description="How thoroughly does the response answer all parts of the question? Score from 1 (incomplete) to 10 (fully comprehensive).",
    )
    reasoning: int = Field(
        ...,
        ge=0,
        le=10,
        description="How well does the response show logical reasoning or step-by-step thought? Score from 1 (poor or no reasoning) to 10 (excellent, structured reasoning).",
    )
    clarity: int = Field(
        ...,
        ge=0,
        le=10,
        description="How clear and well-structured is the language used in the response? Score from 1 (confusing or poorly worded) to 10 (clear and articulate).",
    )
    relevance: int = Field(
        ...,
        ge=0,
        le=10,
        description="How relevant is the response to the original question? Score from 1 (off-topic) to 10 (completely on-topic and focused).",
    )


class Revisor(BaseModel):
    response: str = Field(
        ..., description="The AI-generated answer to the user's question."
    )
    reflection: str = Field(
        ...,
        description=(
            "The agent's self-assessment highlighting flaws or errors in the response, "
            "with concrete examples and suggestions for improvement."
        ),
    )
    citations: List[Citation] = Field(
        ...,
        description="A list of citations referencing external sources that support or validate the revised response.",
    )
    score: Grader = Field(
        ...,
        description="A detailed evaluation of the revised response across correctness, completeness, reasoning, clarity, and relevance.",
    )


# Define all prompt templates

responder_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """
            You are a helpful, honest, and reflective AI assistant.
            
            Current time: {time}
            
            Given a user's question or message, your task is to:

            1. Provide a clear and informative **response** that aims to fully answer the question.
            2. Provide a **reflection** on your own response. Identify any potential flaws, gaps, or improvements. If the response is perfect, explain why. Include specific examples or scenarios where applicable.
            3. Provide a list of **search_queries** that could help enhance or fact-check your response. 
            
            - If the question is trivial or you are confident your answer is fully correct, this list can be empty.    
            
            A trivial question is:
            - Common or conversational (e.g., "How are you?", "What is 2 + 2?")
            - Requires no external tools, research, or deep reasoning to answer
            - Often has a short, straightforward answer

            Your task is also to analyze the latest user message and return:

            1. `is_trivial`: true or false — whether the question is trivial
            """
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
).partial(
    time=lambda: datetime.now().isoformat(),
)


revisor_prompt_template = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            """
            You are a reflective and research-enhanced AI assistant.
            
            Current time: {time}

            Your task is to revise a previously generated answer by improving its accuracy, clarity, and completeness, while incorporating any available external information (such as search results or retrieved documents). You previously generated an answer to a question. Now, you have access to external search results (shown above as prior messages).

            Your revised **response** must:
            - Be more accurate and comprehensive (be very detailed) than the original
            - Reference supporting sources using numbered tags like [1], [2], etc. directly within the text
            - Use the citation numbers to match the `citations` list provided
            - Use the reflection information to make adjustments to the response

            Return a structured JSON object with the following fields:

              1. **response**: The improved and augmented answer. It must include citation tags like [1] placed at relevant points where external sources are referenced.
              2. **reflection**: A self-assessment of the quality and limitations of the new response. Highlight what was improved, what might still be lacking, and how the citations were used.
              3. **search_queries**: A list of follow-up search queries, if any, that the agent would still explore for deeper answers. Leave empty if unnecessary.
              4. **citations**: A list of external sources that support the revised response. Each citation must include:
                - `tag_name`: a short reference name
                - `title`: the full title of the source
                - `description`: a brief (≤ 250 characters) summary of the source
                - `url`: the source link
                - `number`: a unique integer that matches the citation tag in the response
            
            Assess the response based on the following **five criteria**, and return a score between 0 and 10 for each:

            1. **correctness**: How factually accurate is the response?
              - 0 = Completely incorrect
              - 10 = Fully correct with no factual errors

            2. **completeness**: How thoroughly does the response address every part of the question?
              - 0 = Completely incomplete
              - 10 = Fully comprehensive

            3. **reasoning**: How well does the response demonstrate logical thinking or step-by-step explanation?
              - 0 = No reasoning
              - 10 = Clear, structured, insightful reasoning

            4. **clarity**: How clearly is the response communicated?
              - 0 = Confusing or poorly structured
              - 10 = Clear, precise, and well-written

            5. **relevance**: How well does the response stay focused on the original question?
              - 0 = Off-topic
              - 10 = Directly addresses the question with no fluff
           """
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
).partial(
    time=lambda: datetime.now().isoformat(),
)


# Define all chains (Responder, Revisor, and Grader)


responder_chain = responder_prompt_template | llm.bind_tools(
    tools=[Responder], tool_choice="Responder"
)

revisor_chain = revisor_prompt_template | llm.bind_tools(
    tools=[Revisor], tool_choice="Revisor"
)


# Node names

RESPONDER = "responder"
REVISOR = "revisor"
SEARCH_TOOL = "search_tool"
END = "end"


# Create conditional nodes


def get_ai_response(state: List[BaseMessage]) -> Optional[Dict[str, Any]]:
    for message in reversed(state):
        if isinstance(message, AIMessage):
            tool_calls = message.additional_kwargs.get("tool_calls", [])

            if tool_calls:
                try:
                    arguments = json.loads(tool_calls[0]["function"]["arguments"])
                    return arguments
                except (KeyError, json.JSONDecodeError):
                    continue
    return None


def search_results_formatter(search_results):
    lines = []

    for search_result in search_results:
        query = search_result.get("query", "")
        results = search_result.get("results", [])

        lines.append(f"\nSearch Query: {query}")

        for idx, result in enumerate(results, start=1):
            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            content = (
                result.get("content", "No description available")
                .replace("\n", " ")
                .strip()
            )

            lines.append(f"\nResult {idx}:")
            lines.append(f"- Title: {title}")
            lines.append(f"- Description: {content}")
            lines.append(f"- URL: {url}")

    return "\n".join(lines)


def responder_condition_node(state: List[BaseMessage]) -> str:
    response = get_ai_response(state)

    if not response:
        return END

    is_trivial = response.get("is_trivial", False)
    search_queries = response.get("search_queries", [])

    if not is_trivial:
        return SEARCH_TOOL if search_queries else REVISOR

    return END


def search_tool_node(state: List[BaseMessage]) -> List[BaseMessage]:
    last_message: AIMessage = state[-1]

    if not hasattr(last_message, "tool_calls") or not last_message.tool_calls:
        return []

    tool_messages = []

    for tool_call in last_message.tool_calls:
        if tool_call["name"] in ["Responder", "Revisor"]:
            call_id = tool_call["id"]
            search_queries = tool_call["args"].get("search_queries", [])

            query_results = []

            for query in search_queries:
                result = tavily_search.invoke(query)
                query_results.append(result)

            tool_messages.append(
                ToolMessage(
                    content=search_results_formatter(query_results),
                    tool_call_id=call_id,
                )
            )

    return tool_messages


def revisor_condition_node(state: List[BaseMessage]) -> str:
    response = get_ai_response(state)
    score = response.get("score", {})

    print("score", state)

    if all(value == 10 for value in score.values()):
        return END

    else:
        return REVISOR


# Draw graph
graph = MessageGraph()

graph.set_entry_point(RESPONDER)

graph.add_node(RESPONDER, responder_chain)
graph.add_node(REVISOR, revisor_chain)
graph.add_node(SEARCH_TOOL, search_tool_node)
graph.add_node(END, lambda state: state)

graph.add_conditional_edges(RESPONDER, responder_condition_node)
graph.add_edge(SEARCH_TOOL, REVISOR)
graph.add_edge(REVISOR, END)


prompt = "Mention 5 footballers"


app = graph.compile()
app.invoke(prompt)
