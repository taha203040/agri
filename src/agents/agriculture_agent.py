import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os
import logging
from langchain.agents import create_react_agent
from src.config.config import settings
from src.memory.conversation_memory import get_checkpointer
from src.retrieval.retriever import retriever_tool, diseases_tool
logger = logging.getLogger(__name__)

TOOLS = [retriever_tool, diseases_tool]
SYSTEM_PROMPT = (
    "You are a helpful assistant specialized in agriculture. "
    "Use the retriever_tool tool for soil-related questions "
    "and the diseases_tool tool for plant disease questions."
)
 

async def _get_graph(checkpointer=None):
    graph = create_react_agent(
        model=settings.model_name,
        tools=TOOLS,
        prompt=SYSTEM_PROMPT,
        checkpointer=checkpointer,  # ← accepted natively here
    )
    return graph
def _make_config(thread_id: str) -> dict:
    return {"configurable": {"thread_id": thread_id}}


# ── Public API ────────────────────────────────────────────────────────────────

async def stream_response(message: str, thread_id: str = settings.default_thread_id):
    """
    Async generator — yields clean text chunks with memory and tools.
    """
    async with get_checkpointer() as checkpointer: 
        graph = await _get_graph(checkpointer)
        config = _make_config(thread_id)
        user_input = {"messages": [{"role": "user", "content": message}]}

        async for chunk in graph.astream(user_input, config=config, stream_mode="values"):
            last = chunk["messages"][-1]
            # Only yield final AI responses, skip tool call messages
            if last.__class__.__name__ == "AIMessage" and last.content:
                yield last.content


async def invoke_response(message: str, thread_id: str = settings.default_thread_id) -> str:
    """
    Single-shot async call — returns the final AI response as a string.
    """
    async with get_checkpointer() as checkpointer:
        graph = await _get_graph(checkpointer)
        config = _make_config(thread_id)
        user_input = {"messages": [{"role": "user", "content": message}]}

        result = await graph.ainvoke(user_input, config=config)
        ai_messages = [
            m.content for m in result["messages"]
            if m.__class__.__name__ == "AIMessage" and m.content
        ]
        return ai_messages[-1] if ai_messages else "No response generated."

