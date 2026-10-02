from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from src.config.settings import settings


def get_checkpointer_context():
    """
    Return an async context manager for the Postgres checkpointer.

    Usage:
        async with get_checkpointer_context() as checkpointer:
            await checkpointer.setup()
            agent = create_agriculture_agent(model, checkpointer=checkpointer)
            ...

    The connection stays open for the entire `async with` block and is
    closed automatically on exit.
    """
    return AsyncPostgresSaver.from_conn_string(settings.db_uri)