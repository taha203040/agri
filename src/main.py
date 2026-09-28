from src.config.config import agent
from src.agents.service import stream_response
import asyncio
async def main():
    response = agent.invoke({
        "messages": [
            ("user", "What is crop rotation?")
        ]
    })

    async for chunk in stream_response("What are the diseases of tomato?"):
        print(chunk, end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())