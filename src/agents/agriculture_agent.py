import logging

from src.config.config import settings
from src.retrieval.retriever import retriever_tool, diseases_tool

from langgraph.prebuilt import create_react_agent

logger = logging.getLogger(__name__)

TOOLS = [retriever_tool, diseases_tool]

SYSTEM_PROMPT = (
    "You are a helpful assistant specialized in agriculture. "
    "Use the retriever_tool tool for soil-related questions "
    "and the diseases_tool tool for plant disease questions."
)


def _get_graph():
    graph = create_react_agent(
        model=settings.model_name,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
    )

    return graph


# ── Public API ────────────────────────────────────────────────────────────────

async def stream_response(message: str):
    """
    Async generator — yields text chunks without conversation persistence.
    """
    graph = _get_graph()

    user_input = {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ]
    }

    async for chunk in graph.astream(
        user_input,
        stream_mode="values",
    ):
        last = chunk["messages"][-1]

        # Only yield AI responses, skip tool call messages
        if last.__class__.__name__ == "AIMessage" and last.content:
            yield last.content


async def invoke_response(message: str) -> str:
    """
    Single-shot async call — returns the final AI response.
    """
    graph = _get_graph()

    user_input = {
        "messages": [
            {
                "role": "user",
                "content": message,
            }
        ]
    }

    result = await graph.ainvoke(user_input)

    ai_messages = [
        m.content
        for m in result["messages"]
        if m.__class__.__name__ == "AIMessage" and m.content
    ]

    return ai_messages[-1] if ai_messages else "No response generated."