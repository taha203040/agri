from src.agents.agriculture_graph import build_agriculture_graph


def create_agriculture_agent(model, checkpointer=None):
    """
    Create the agriculture agent.

    Returns a compiled LangGraph Runnable (custom StateGraph) that
    exposes the same interface as `create_agent()`: .invoke / .ainvoke /
    .stream / .astream_events, with checkpointer-based memory.
    """
    return build_agriculture_graph(
        model=model,
        checkpointer=checkpointer,
    )
# from langchain.agents import create_agent

# from src.retrieval.retriever import TOOLS
# def create_agriculture_agent(model,checkpointer=None):
#     """
#     Create the agriculture agent with access
#     to the agricultural retrieval tools.
#     """
#     return create_agent(
#         model=model,
#         tools=TOOLS,
#         checkpointer=checkpointer
#     )

