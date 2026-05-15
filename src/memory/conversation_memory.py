# from langchain.chat_models import init_chat_model
# from langgraph.graph import StateGraph, MessagesState, START
# from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
# from dotenv import load_dotenv
# import asyncio
# import sys

# load_dotenv()

# model = init_chat_model(model="deepseek-chat")

# DB_URI = "postgresql://postgres:0000@localhost:5432/myagri"

# async def memoryManager(message):

#     async with AsyncPostgresSaver.from_conn_string(DB_URI) as checkpointer:

#         await checkpointer.setup()

#         async def call_model(state: MessagesState):
#             response = await model.ainvoke(state["messages"])
#             return {"messages": response}

#         builder = StateGraph(MessagesState)

#         builder.add_node("call_model", call_model)
#         builder.add_edge(START, "call_model")

#         graph = builder.compile(checkpointer=checkpointer)

#         config = {
#             "configurable": {
#                 "thread_id": "1"
#             }
#         }

#         async for chunk in graph.astream(
#             {"messages": [{"role": "user", "content": message}]},
#             config=config,
#             stream_mode="values"
#         ):
#             chunk["messages"][-1].pretty_print()

# if sys.platform == "win32":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# asyncio.run(memoryManager("is there a way to create for me a simple as you can an overview what can i do with it"))\
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from src.config.config import settings

from contextlib import asynccontextmanager
@asynccontextmanager                          # ← add this

async def get_checkpointer(): 
    """
    Async context manager — use with `async with get_checkpointer() as cp`.
    Handles setup automatically.
    """
    async with AsyncPostgresSaver.from_conn_string(settings.db_uri) as checkpointer:
        await checkpointer.setup()
        yield checkpointer