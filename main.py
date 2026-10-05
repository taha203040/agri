import asyncio
import sys

# ── Windows: psycopg async needs SelectorEventLoop, not ProactorEventLoop ──
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

from src.config.settings import settings
from src.memory.conversation_memory import get_checkpointer_context
from src.agents.agriculture_agent import create_agriculture_agent
from src.agents.service import invoke_response, stream_response
load_dotenv()

async def main():
    async with get_checkpointer_context() as checkpointer:
        await checkpointer.setup()

        model = ChatDeepSeek(
            model=settings.model_name,
            api_key=settings.deepseek_api_key,
        )
        agent = create_agriculture_agent(model=model, checkpointer=checkpointer)

        thread_id = "cli-demo-8"

        # print("─── invoke ───")
        # answer = await invoke_response(agent, "when we use big amount of water ?", thread_id)
        # print(answer)

        print("\n─── stream ───")
        async for chunk in stream_response(
            agent, "what does the retriver cover about the water ?", thread_id
        ):
            print(chunk, end="", flush=True)
        print()

        # print("\n─── follow-up (same thread) ───")
        # async for chunk in stream_response(
        #     agent, "What about their treatment?", thread_id
        # ):
        #     print(chunk, end="", flush=True)
        # print()


if __name__ == "__main__":
    asyncio.run(main())