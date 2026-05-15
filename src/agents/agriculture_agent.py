# from langchain.agents import create_agent
# from src.retrieval.retriever import retriever_tool, diseases_tool
# from dotenv import load_dotenv
# import json
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# load_dotenv()

# class AgricultureAgent:
#     """Agriculture Agent wrapper for handling farming-related queries"""
    
#     def __init__(self):
#         self.agent = create_agent(
#             model='deepseek-chat',
#             tools=[retriever_tool, diseases_tool],
#             system_prompt='You are a helpful assistant specialized in the agriculture field. Answer just the questions related to soil samples using the soil_retriever tool and diseases using the disease_retriever tool.'
#         )
    
#     def stream(self, question_input):
#         """Stream agent responses with proper chunk formatting"""
#         try:
#             if hasattr(self.agent, 'stream'):
#                 for chunk in self.agent.stream(question_input):
#                     yield self._format_chunk(chunk)
#             else:
#                 logger.warning("Agent doesn't support streaming, simulating...")
#                 yield from self._simulate_stream(question_input)
#         except Exception as e:
#             logger.error(f"Stream error: {e}")
#             yield {"type": "error", "error": str(e)}
    
#     def _format_chunk(self, chunk):
#         """Format a chunk into a standard dict"""
#         if isinstance(chunk, dict):
#             return chunk
#         if hasattr(chunk, 'dict'):
#             return chunk.dict()
#         if hasattr(chunk, 'content'):
#             return {"type": "token", "content": chunk.content}
#         return {"type": "token", "content": str(chunk)}

#     def _simulate_stream(self, question_input):
#         """Simulate streaming by splitting the response"""
#         result = self.agent.invoke(question_input)
#         for msg in result.get('messages', []):
#             if getattr(msg, 'type', None) == 'ai' or msg.__class__.__name__ == 'AIMessage':
#                 content = msg.content if hasattr(msg, 'content') else str(msg)
#                 words = content.split()
#                 for i, word in enumerate(words):
#                     yield {"type": "token", "content": word + (" " if i < len(words)-1 else "")}
#                 break
#         yield {"type": "done"}
#     def invoke(self, question_input):
#         """Invoke agent without streaming"""
#         return self.agent.invoke(question_input)
    
#     def run(self, question: str):
#         """Run agent and return AI messages"""
#         question_input = {'messages': [{'role': 'user', 'content': question}]}
#         answer = self.agent.invoke(question_input)
#         ai_messages = [msg.content for msg in answer['messages'] 
#                       if msg.__class__.__name__ == 'AIMessage']
        
#         for i, msg in enumerate(ai_messages, 1):
#             logger.info(f"AI message {i}: {msg}")
        
#         return ai_messages

# # Create a singleton instance for reuse
# agriculture_agent = AgricultureAgent()
# import logging
# from langchain.agents import create_agent
# from langgraph.graph import StateGraph, MessagesState, START
# from src.config.config import settings
# from src.memory.conversation_memory import get_checkpointer
# from src.retrieval.retriever import retriever_tool, diseases_tool

# logger = logging.getLogger(__name__)

# SYSTEM_PROMPT = (
#     "You are a helpful assistant specialized in agriculture. "
#     "Use the soil_retriever tool for soil-related questions "
#     "and the disease_retriever tool for plant disease questions."
# )

# TOOLS = [retriever_tool, diseases_tool]


# def _build_graph(checkpointer=None):
#     """
#     Build the LangGraph agent graph.
#     Pass a checkpointer to enable memory persistence.
#     """
#     base_agent = create_agent(
#         model=settings.model_name,
#         tools=TOOLS,
#         system_prompt=SYSTEM_PROMPT,
#     )

#     async def call_model(state: MessagesState):
#         response = await base_agent.ainvoke(state)
#         return {"messages": response["messages"]}

#     builder = StateGraph(MessagesState)
#     builder.add_node("call_model", call_model)
#     builder.add_edge(START, "call_model")

#     return builder.compile(checkpointer=checkpointer)


# def _make_config(thread_id: str) -> dict:
#     return {"configurable": {"thread_id": thread_id}}


# # ── Public API ──────────────────────────────────────────────────────────────

# async def stream_response(message: str, thread_id: str = settings.default_thread_id):
#     """
#     Async generator — yields clean text chunks with memory.
#     Usage:
#         async for chunk in stream_response("How to treat rust?", thread_id="user-42"):
#             print(chunk)
#     """
#     async with get_checkpointer() as checkpointer:
#         graph = _build_graph(checkpointer)
#         config = _make_config(thread_id)
#         user_input = {"messages": [{"role": "user", "content": message}]}

#         async for chunk in graph.astream(user_input, config=config, stream_mode="values"):
#             last = chunk["messages"][-1]
#             content = last.content if hasattr(last, "content") else str(last)
#             if content:
#                 yield content


# async def invoke_response(message: str, thread_id: str = settings.default_thread_id) -> str:
#     """
#     Single-shot async call — returns the final AI response as a string.
#     """
#     async with get_checkpointer() as checkpointer:
#         graph = _build_graph(checkpointer)
#         config = _make_config(thread_id)
#         user_input = {"messages": [{"role": "user", "content": message}]}

#         result = await graph.ainvoke(user_input, config=config)
#         ai_messages = [
#             m.content for m in result["messages"]
#             if m.__class__.__name__ == "AIMessage"
#         ]
#         return ai_messages[-1] if ai_messages else "No response generated."
# src/agents/agriculture_agent.py

import logging
from langchain.agents import create_agent
from src.config.config import settings
from src.memory.conversation_memory import get_checkpointer
from src.retrieval.retriever import retriever_tool, diseases_tool
from langgraph.prebuilt import create_react_agent  # ← not from langchain

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