from dotenv import load_dotenv
import operator
from typing import TypedDict, List, Annotated
from langgraph.graph import graph, StateGraph, END

load_dotenv()

INCREMENT = "increment"


class State(TypedDict):
    count: int
    sum: Annotated[int, operator.add]
    history: Annotated[List[int], operator.concat]


def increment(state: State) -> State:
    new_count = state["count"] + 1
    return {"count": new_count, "sum": new_count, "history": [new_count]}


def should_continue(state: State) -> State:
    if state["count"] < 10:
        return INCREMENT

    return END


graph = StateGraph(State)

graph.set_entry_point(INCREMENT)
graph.add_node(INCREMENT, increment)
graph.add_conditional_edges(INCREMENT, should_continue)

app = graph.compile()

state = {"count": 0, "sum": 0, "history": []}
response = app.invoke(state)

print("response", response)
