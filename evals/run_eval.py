import asyncio
import sys
import os

# Windows: psycopg async needs SelectorEventLoop
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load LangSmith env vars
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_PROJECT", "agri-rag-eval")

from langchain_deepseek import ChatDeepSeek
from langsmith import Client

from src.config.settings import settings
from src.memory.conversation_memory import get_checkpointer_context
from src.agents.agriculture_agent import create_agriculture_agent

from evals.config import DATASET_NAME
from evals.dataset import get_or_create_dataset
from evals.target import make_target
from evals.evaluators import (
    helpfulness_judge,
    groundedness_judge,
    retrieval_relevance_judge,
)


async def main():
    client = Client()

    # 1. Ensure the dataset exists
    dataset = get_or_create_dataset(client)

    # 2. Open checkpointer + build agent (same as your app)
    async with get_checkpointer_context() as checkpointer:
        await checkpointer.setup()

        model = ChatDeepSeek(
            model=settings.model_name,
            api_key=settings.deepseek_api_key,
        )
        agent = create_agriculture_agent(model=model, checkpointer=checkpointer)

        # 3. Build the target function
        target = make_target(agent)

        # 4. Run the experiment
        print(f"\n🚀 Running evaluation on dataset: {DATASET_NAME}\n")

        results = await client.aevaluate(
            target,
            data=dataset.name,
            evaluators=[
                helpfulness_judge,
                groundedness_judge,
                retrieval_relevance_judge,
            ],
            experiment_prefix="agri-rag-baseline",
            metadata={
                "version": "hybrid-retrieval-v1",
                "judge": "deepseek-chat",
            },
            max_concurrency=2,
        )

        # 5. Print summary
        print("\n📊 Results:")
        print(results)

        # Optional: convert to pandas if installed
        try:
            df = results.to_pandas()
            print("\n📈 Per-example results:")
            print(df[["inputs.question", "feedback.helpfulness", "feedback.groundedness", "feedback.retrieval_relevance"]])
        except Exception:
            pass


if __name__ == "__main__":
    asyncio.run(main())