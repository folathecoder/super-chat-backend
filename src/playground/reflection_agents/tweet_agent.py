from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, MessageGraph
from langchain_core.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

generation_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a tweet writer in the tech niche. Your job is to compose the best tweets that drive engagement and resonate with a technical audience. Generate the best tweet possible and if the user provides a critique, respond with a revised version. Improve with each critique."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

refection_prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessagePromptTemplate.from_template(
            "You are a tweet critique. Assess tweets and suggest improvements in detail. Use examples."
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro")

generation_chain = generation_prompt | llm
refection_chain = refection_prompt | llm

# A MessageGraph in LangGraph is a simplified graph structure where the state is just a list of chat messages, and each node processes those messages to return new ones, making it easy to build chat-based agents.

graph = MessageGraph()

# Create the generate and reflect node
REFLECT = "reflect"
GENERATE = "generate"


def generate_node(state):
    return generation_chain.invoke({"messages": state})


def reflect_node(state):
    response = refection_chain.invoke({"messages": state})
    return [HumanMessage(content=response.content)]


# Add nodes to graph
graph.add_node(GENERATE, generate_node)
graph.add_node(REFLECT, reflect_node)

# Set the entry point of the graph
graph.set_entry_point(GENERATE)


def should_continue(state):
    if len(state) > 6:
        return END

    return REFLECT


graph.add_conditional_edges(GENERATE, should_continue)
graph.add_edge(REFLECT, GENERATE)

app = graph.compile()

print(app.get_graph().draw_mermaid())
app.get_graph().print_ascii()

response = app.invoke(
    HumanMessage(
        content="What is the Future of Software Engineering and how AI will affect the industry?"
    )
)
print(response)
