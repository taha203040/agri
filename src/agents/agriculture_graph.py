from typing import Annotated, Literal, TypedDict
import operator

from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage
from langchain_core.runnables import Runnable
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langsmith import traceable
from src.retrieval.retriever import (
    water_retriever,
    crop_health_retriever,
    yield_retriever,
)


# ──────────────────────────────────────────────────────────────────────────────
# State
# ──────────────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    # `operator.add` lets parallel nodes append without overwriting each other
    context: Annotated[list[str], operator.add]


# ──────────────────────────────────────────────────────────────────────────────
# Node 1: classify intent
# ──────────────────────────────────────────────────────────────────────────────

def classify_intent(state: AgentState) -> dict:
    """
    Decide which retriever(s) to run based on the last user message.
    Could also be an LLM call — rules are fine and cheaper.
    """
    q = state["messages"][-1].content.lower()

    intents = []
    if any(k in q for k in ["water", "irrigation", "moisture", "rain"]):
        intents.append("water")
    if any(k in q for k in ["disease", "pest", "health", "leaf", "fungus"]):
        intents.append("crop_health")
    if any(k in q for k in ["yield", "harvest", "production", "forecast"]):
        intents.append("yield")

    # default: run all
    if not intents:
        intents = ["water", "crop_health", "yield"]

    return {"intent": ",".join(intents)}


# ──────────────────────────────────────────────────────────────────────────────
# Node 2/3/4: retrievers (each is its own node)
# ──────────────────────────────────────────────────────────────────────────────
def water_node(state: AgentState) -> dict:
    query = state["messages"][-1].content
    docs = water_retriever.invoke(query)
    return {"context": [f"[water] {d.page_content}" for d in docs]}


def crop_health_node(state: AgentState) -> dict:
    query = state["messages"][-1].content
    docs = crop_health_retriever.invoke(query)
    return {"context": [f"[crop_health] {d.page_content}" for d in docs]}


def yield_node(state: AgentState) -> dict:
    query = state["messages"][-1].content
    docs = yield_retriever.invoke(query)
    return {"context": [f"[yield] {d.page_content}" for d in docs]}


# ──────────────────────────────────────────────────────────────────────────────
# Node 5: synthesize answer with LLM
# ──────────────────────────────────────────────────────────────────────────────
def synthesize(state: AgentState, config) -> dict:
    model: Runnable = config["configurable"]["model"]

    context_block = "\n\n".join(state.get("context", [])) or "(no context retrieved)"

    system = SystemMessage(
        content=(
            "You are an agriculture assistant. "
            "Use the retrieved context to answer the farmer's question. "
            "If the context doesn't cover the question, say so.\n\n"
            f"--- Retrieved context ---\n{context_block}"
        )
    )

    response = model.invoke([system] + state["messages"])
    return {"messages": [response]}


# ──────────────────────────────────────────────────────────────────────────────
# Conditional routing after classify
# ──────────────────────────────────────────────────────────────────────────────
def route_retrievers(state: AgentState) -> list[str]:
    """
    Return a list of node names to run in parallel.
    LangGraph executes them concurrently and merges state via `operator.add`.
    """
    routes = []
    intents = state["intent"].split(",")

    if "water" in intents:
        routes.append("water_node")
    if "crop_health" in intents:
        routes.append("crop_health_node")
    if "yield" in intents:
        routes.append("yield_node")

    return routes or ["water_node", "crop_health_node", "yield_node"]


# ──────────────────────────────────────────────────────────────────────────────
# Build the graph
# ──────────────────────────────────────────────────────────────────────────────
def build_agriculture_graph(model, checkpointer=None):
    builder = StateGraph(AgentState)

    # nodes
    builder.add_node("classify", classify_intent)
    builder.add_node("water_node", water_node)
    builder.add_node("crop_health_node", crop_health_node)
    builder.add_node("yield_node", yield_node)
    builder.add_node("synthesize", synthesize)

    # edges
    builder.add_edge(START, "classify")

    # fan-out: after classify, run one or more retrievers in parallel
    builder.add_conditional_edges(
        "classify",
        route_retrievers,
        ["water_node", "crop_health_node", "yield_node"],
    )

    # fan-in: all retrievers go to synthesize
    builder.add_edge("water_node", "synthesize")
    builder.add_edge("crop_health_node", "synthesize")
    builder.add_edge("yield_node", "synthesize")

    builder.add_edge("synthesize", END)

    graph = builder.compile(checkpointer=checkpointer)
    return graph.with_config({"configurable": {"model": model}})