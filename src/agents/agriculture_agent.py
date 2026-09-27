from langgraph.agents import create_react_agent

from src.retrieval.retriever import TOOLS


def create_agent(model):
    return create_react_agent(
        model=model,
        tools=TOOLS,
    )