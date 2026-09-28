from langchain_deepseek import ChatDeepSeek

from src.config.settings import settings
from src.agents.agriculture_agent import create_agriculture_agent

model = ChatDeepSeek(
    model=settings.model_name,
    api_key=settings.deepseek_api_key,
)

# checkpointer = get_checkpointer()

agent = create_agriculture_agent(
    model=model
)