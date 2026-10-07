from langchain_deepseek import ChatDeepSeek

from src.config.settings import settings

from dotenv import load_dotenv
load_dotenv()

DATASET_NAME = "agri-rag-eval"

# Judge model — uses DeepSeek since that's your only API.
# If you later add OpenAI/Anthropic, swap here.
JUDGE_MODEL = ChatDeepSeek(
    model="deepseek-chat",
    api_key=settings.deepseek_api_key,
)