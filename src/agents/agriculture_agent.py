from langchain.agents import create_agent

from src.retrieval.retriever import TOOLS
def create_agriculture_agent(model,checkpointer=None):
    """
    Create the agriculture agent with access
    to the agricultural retrieval tools.
    """
    return create_agent(
        model=model,
        tools=TOOLS,
        checkpointer=checkpointer
    )

