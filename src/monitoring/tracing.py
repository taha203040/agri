import os

from src.config.settings import settings


def setup_tracing() -> None:
    """LangSmith reads os.environ, not pydantic settings."""
    os.environ["LANGSMITH_TRACING"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project
