import asyncio

import uvicorn

if __name__ == "__main__":
    # Windows: psycopg async needs SelectorEventLoop, but uvicorn defaults to
    # ProactorEventLoop there and ignores the event loop policy.
    config = uvicorn.Config("src.api.app:app", host="127.0.0.1", port=8000)
    server = uvicorn.Server(config)
    asyncio.run(server.serve(), loop_factory=asyncio.SelectorEventLoop)
