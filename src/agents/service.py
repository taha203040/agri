import logging

from src.config.config import settings
from src.config.config import agent
# from src.memory.conversation_memory import get_checkpointer

print("✅✅✅✅✅",settings.model_name)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Agent setup
# ──────────────────────────────────────────────────────────────────────────────

# checkpointer = get_checkpointer()



# ──────────────────────────────────────────────────────────────────────────────
# Invoke
# ──────────────────────────────────────────────────────────────────────────────

async def invoke_response(
    question: str,
    # thread_id: str,
) -> str:
    """
    Run the agriculture agent and return the final response.
    Conversation state is persisted using thread_id.
    """

    # config = {
    #     "configurable": {
    #         "thread_id": thread_id,
    #     }
    # }

    result = await agent.ainvoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        },
        # config=config,
    )

    messages = result.get("messages", [])

    if not messages:
        return ""

    return messages[-1].content


# ──────────────────────────────────────────────────────────────────────────────
# Streaming
# ──────────────────────────────────────────────────────────────────────────────

async def stream_response(
    question: str,
    # thread_id: str,
):
    """
    Stream the agriculture agent response.
    Conversation state is persisted using thread_id.
    """

    # config = {
    #     "configurable": {
    #         "thread_id": thread_id,
    #     }
    # }

    async for event in agent.astream_events(
        {
            "messages": [
                {
                    "role": "user",
                    "content": question,
                }
            ]
        },
        # config=config,
        version="v2",
    ):
        if event["event"] != "on_chat_model_stream":
            continue

        chunk = event["data"]["chunk"]

        if not chunk.content:
            continue

        yield chunk.content
