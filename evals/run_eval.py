import asyncio
import json
import sys
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

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
from evals.dataset import get_or_create_dataset, TOPIC_BY_QUESTION
from evals.target import make_target
from evals.evaluators import (
    helpfulness_evaluator,
    groundedness_evaluator,
    retrieval_relevance_evaluator,
    correctness_evaluator,
)

RESULTS_DIR = Path(__file__).parent / "results"


async def summarize(results) -> dict:
    """Mean score per metric, overall and per topic (True/False count as 1/0)."""
    scores: dict[str, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))

    async for row in results:
        question = row["example"].inputs.get("question", "")
        topic = (row["example"].metadata or {}).get("topic") or TOPIC_BY_QUESTION.get(question, "unknown")
        for r in row["evaluation_results"]["results"]:
            if r.score is None:
                continue
            scores["all"][r.key].append(float(r.score))
            scores[topic][r.key].append(float(r.score))

    return {
        topic: {
            metric: {"mean": round(sum(v) / len(v), 3), "n": len(v)}
            for metric, v in metrics.items()
        }
        for topic, metrics in scores.items()
    }


def print_summary(summary: dict) -> None:
    metrics = sorted({m for t in summary.values() for m in t})
    print(f"\n{'topic':<12}" + "".join(f"{m:>22}" for m in metrics))
    for topic in sorted(summary, key=lambda t: (t != "all", t)):
        row = "".join(
            f"{summary[topic][m]['mean']:>16.2f} (n={summary[topic][m]['n']:<2})" if m in summary[topic] else f"{'-':>22}"
            for m in metrics
        )
        print(f"{topic:<12}{row}")


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
            extra_body={"thinking": {"type": "disabled"}}  # Key: disable thinking mode
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
                helpfulness_evaluator,
                groundedness_evaluator,
                retrieval_relevance_evaluator,
                correctness_evaluator,
            ],
            experiment_prefix="agri-rag-baseline",
            metadata={
                "version": "hybrid-retrieval-v1",
                "judge": "deepseek-chat",
            },
            max_concurrency=2,
        )

        # 5. Summarize (overall + per topic) and save so runs can be compared
        summary = await summarize(results)
        print("\n📊 Results (mean score, 1.0 = all passed):")
        print_summary(summary)

        RESULTS_DIR.mkdir(exist_ok=True)
        out = RESULTS_DIR / f"{datetime.now():%Y%m%d-%H%M%S}.json"
        out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
        print(f"\n💾 Saved to {out}")


if __name__ == "__main__":
    asyncio.run(main())
