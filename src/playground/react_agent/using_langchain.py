from dotenv import load_dotenv
from datetime import datetime
from langchain.agents import initialize_agent
from langchain_openai import ChatOpenAI
from langchain_community.tools import TavilySearchResults, tool

load_dotenv()

search_tool = TavilySearchResults(search_depth="basic")


@tool
def get_current_time(date_format: str) -> str:
    """
    Returns the current time formatted according to the provided format string.

    Args:
        date_format (str): The format string following datetime.strftime conventions.

    Returns:
        str: Formatted current time.
    """
    try:
        current_time = datetime.now()
        return current_time.strftime(date_format)
    except Exception as e:
        return f"Error formatting date: {e}"


llm = ChatOpenAI(model="gpt-4o")

agent = initialize_agent(
    tools=[search_tool, get_current_time],
    llm=llm,
    agent="zero-shot-react-description",
    verbose=True,
)

result = agent.invoke("Explain in details, how to become a Software Engineer.")

print("result", result)
print("=== Agent Final Answer ===")
print(result["output"])
