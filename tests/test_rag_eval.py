import asyncio
import sys
import uuid

import pytest
from langsmith import testing as t

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from langchain_deepseek import ChatDeepSeek

from src.config.settings import settings
from src.memory.conversation_memory import get_checkpointer_context
from src.agents.agriculture_agent import create_agriculture_agent

from evals.target import extract_documents
from evals.evaluators import (
    helpfulness_judge,
    groundedness_judge,
    retrieval_relevance_judge,
)


# ──────────────────────────────────────────────────────────────────────────────
# Sync helper — runs the agent fresh per test (isolated state)
# ──────────────────────────────────────────────────────────────────────────────

def run_agent(question: str) -> dict:
    async def _run():
        async with get_checkpointer_context() as checkpointer:
            await checkpointer.setup()
            model = ChatDeepSeek(
                model=settings.model_name,
                api_key=settings.deepseek_api_key,
            )
            agent = create_agriculture_agent(model=model, checkpointer=checkpointer)
            config = {"configurable": {"thread_id": f"test-{uuid.uuid4()}"}}
            result = await agent.ainvoke(
                {"messages": [{"role": "user", "content": question}]},
                config=config,
            )
            return {
                "answer": result["messages"][-1].content,
                "documents": extract_documents(result),
            }

    return asyncio.run(_run())


# ──────────────────────────────────────────────────────────────────────────────
# Tests
# ──────────────────────────────────────────────────────────────────────────────

@pytest.mark.langsmith
def test_helpfulness():
    inputs = {"question": "How much water does maize need per growing season?"}
    outputs = run_agent(inputs["question"])

    t.log_inputs(inputs)
    t.log_outputs({"answer": outputs["answer"]})

    helpfulness_judge(
        inputs=inputs,
        outputs={"answer": outputs["answer"]},
    )


@pytest.mark.langsmith
def test_groundedness():
    inputs = {"question": "What are the symptoms of early blight in tomato?"}
    outputs = run_agent(inputs["question"])

    t.log_inputs(inputs)
    t.log_outputs({"answer": outputs["answer"]})
    t.log_metadata({"num_documents": len(outputs["documents"])})

    groundedness_judge(
        context={"documents": outputs["documents"]},
        outputs={"answer": outputs["answer"]},
    )


@pytest.mark.langsmith
def test_retrieval_relevance():
    inputs = {"question": "Which nutrients are deficient in sandy soil?"}
    outputs = run_agent(inputs["question"])

    t.log_inputs(inputs)
    t.log_outputs({"answer": outputs["answer"]})

    retrieval_relevance_judge(
        inputs=inputs,
        context={"documents": outputs["documents"]},
    )