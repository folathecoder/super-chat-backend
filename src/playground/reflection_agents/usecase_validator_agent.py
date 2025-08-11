import json
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langgraph.graph import END, MessageGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)

load_dotenv()

GENERATE = "generate"
REFLECT = "reflect"
SCORE = "score"

MINIMUM_SCORE = 8


class Score(BaseModel):
    clarity: int = Field(..., description="How clearly is the use case defined? (1–10)")
    feasibility: int = Field(
        ...,
        description="How realistic is the idea to implement with current technology? (1–10)",
    )
    value: int = Field(
        ..., description="How valuable or impactful is the idea to the end user? (1–10)"
    )


generate_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are an AI startup analyst. Your job is to take a user's raw idea for an AI product and transform it into a structured use case.\n\n"
            "Use the following format:\n"
            "- **Target User:**\n"
            "- **Problem:**\n"
            "- **Proposed Solution:**\n"
            "- **How AI Helps:**\n\n"
            "Ensure the summary is concise, but clear and specific. Avoid buzzwords and make it understandable to both technical and business stakeholders. If the user provides a critique, respond with a revised version. Improve with each critique."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

reflect_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a critical AI product reviewer. Your job is to analyze the proposed use case and offer detailed, honest feedback.\n\n"
            "Critique the use case using the following sections:\n"
            "## Clarity\n"
            "- Is the use case well-defined?\n"
            "- Are the user and problem clearly described?\n\n"
            "## Feasibility\n"
            "- Can the solution realistically be implemented with current technology?\n"
            "- Are there missing details that affect feasibility?\n\n"
            "## Value\n"
            "- Does this solve a real user pain point?\n"
            "- Is the value proposition strong or weak?\n\n"
            "Be as detailed as possible and provide suggestions for improvement in each section."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

score_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are an AI use case evaluator. Based on the critique, assign scores from 1 to 10 in the following areas:\n\n"
            "- **Clarity:** How clearly is the use case defined?\n"
            "- **Feasibility:** How realistic is it to build?\n"
            "- **Value:** How impactful or useful is this product idea?\n\n"
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)


llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

generation_chain = generate_prompt | llm
reflection_chain = reflect_prompt | llm
score_chain = score_prompt | llm.with_structured_output(Score)


# Construct the nodes
def generate_node(state):
    return generation_chain.invoke({"messages": state})


def reflect_node(state):
    response = reflection_chain.invoke({"messages": state})
    return [HumanMessage(content=response.content)]


def score_node(state):
    score_obj = score_chain.invoke({"messages": state})
    return [AIMessage(content=score_obj.model_dump_json())]


# Construct the conditional nodes
def should_continue(state):
    score_message = state[-1]
    score_content = json.loads(score_message.content)
    score = Score(**score_content)

    if (
        score.clarity < MINIMUM_SCORE
        or score.feasibility < MINIMUM_SCORE
        or score.value < MINIMUM_SCORE
    ):
        return GENERATE

    return END


graph = MessageGraph()

# Define all nodes
graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)
graph.add_node(SCORE, score_node)

# Where the graph starts
graph.set_entry_point(GENERATE)

# Connect node by creating edges
graph.add_edge(GENERATE, REFLECT)
graph.add_edge(REFLECT, SCORE)
graph.add_conditional_edges(SCORE, should_continue)

app = graph.compile()

print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

response = app.invoke(
    HumanMessage(
        content="I want to build an AI Agent aggregator website to allow users find the best AI Agents for their projects."
    )
)
print(response)
