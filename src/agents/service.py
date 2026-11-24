import logging
from uuid import UUID

from langchain_core.runnables import Runnable

logger = logging.getLogger(__name__)


def _config(thread_id: UUID) -> dict:
    """Run config shared by invoke and stream (memory key + LangSmith labels)."""
    return {
        "configurable": {"thread_id": str(thread_id)},
        "run_name": "agri-chat",
        "tags": ["agri-api"],
        "metadata": {"thread_id": str(thread_id)},
    }


# ──────────────────────────────────────────────────────────────────────────────
# Invoke
# ──────────────────────────────────────────────────────────────────────────────

async def invoke_response(
    agent: Runnable,
    question: str,
    thread_id: UUID,
) -> str:
    """
    Run the agriculture agent and return the final response.
    Conversation state is persisted using thread_id.
    """
    result = await agent.ainvoke(
        {"messages": [{"role": "user", "content": question}]},
        config=_config(thread_id),
    )

    messages = result.get("messages", [])
    if not messages:
        return ""

    return messages[-1].content


# ──────────────────────────────────────────────────────────────────────────────
# Streaming
# ──────────────────────────────────────────────────────────────────────────────

async def stream_response(
    agent: Runnable,
    question: str,
    thread_id: UUID,
):
    """
    Stream the agriculture agent response.
    Conversation state is persisted using thread_id.
    """
    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": question}]},
        config=_config(thread_id),
        version="v2",
    ):
        if event["event"] != "on_chat_model_stream":
            continue

        chunk = event["data"]["chunk"]

        if not chunk.content:
            continue

        yield chunk.content
