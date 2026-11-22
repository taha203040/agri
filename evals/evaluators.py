from openevals.llm import create_llm_as_judge
from openevals.prompts import (
    CORRECTNESS_PROMPT,
    RAG_HELPFULNESS_PROMPT,
    RAG_GROUNDEDNESS_PROMPT,
    RAG_RETRIEVAL_RELEVANCE_PROMPT,
)

from evals.config import JUDGE_MODEL


helpfulness_judge = create_llm_as_judge(
    prompt=RAG_HELPFULNESS_PROMPT,
    feedback_key="helpfulness",
    judge=JUDGE_MODEL,          # ← use judge=, not model=
)

groundedness_judge = create_llm_as_judge(
    prompt=RAG_GROUNDEDNESS_PROMPT,
    feedback_key="groundedness",
    judge=JUDGE_MODEL,
)

retrieval_relevance_judge = create_llm_as_judge(
    prompt=RAG_RETRIEVAL_RELEVANCE_PROMPT,
    feedback_key="retrieval_relevance",
    judge=JUDGE_MODEL,
)

# Compares the answer with the reference answer stored in the dataset.
correctness_judge = create_llm_as_judge(
    prompt=CORRECTNESS_PROMPT,
    feedback_key="correctness",
    judge=JUDGE_MODEL,
)


# ──────────────────────────────────────────────────────────────────────────────
# Dataset-run evaluators (used by `client.aevaluate` in run_eval.py)
#
# LangSmith only hands evaluators `inputs`, `outputs` and `reference_outputs`.
# The groundedness / retrieval-relevance prompts also need `{context}`, so these
# thin wrappers pull the retrieved documents out of the target's `outputs`
# (`{"answer": ..., "documents": [...]}`) and pass them on as `context`.
# The raw judges above are unchanged and still used directly by the pytest tests.
# ──────────────────────────────────────────────────────────────────────────────

def _failed(key: str, outputs: dict) -> dict | None:
    """Score a target error as a failure instead of asking the judge to grade it."""
    answer = outputs.get("answer", "")
    if isinstance(answer, str) and answer.startswith("ERROR:"):
        return {"key": key, "score": False, "comment": answer}
    return None


def helpfulness_evaluator(inputs: dict, outputs: dict) -> dict:
    return _failed("helpfulness", outputs) or helpfulness_judge(
        inputs=inputs,
        outputs={"answer": outputs["answer"]},
    )


def groundedness_evaluator(inputs: dict, outputs: dict) -> dict:
    return _failed("groundedness", outputs) or groundedness_judge(
        context={"documents": outputs.get("documents", [])},
        outputs={"answer": outputs["answer"]},
    )


def retrieval_relevance_evaluator(inputs: dict, outputs: dict) -> dict:
    return _failed("retrieval_relevance", outputs) or retrieval_relevance_judge(
        inputs=inputs,
        context={"documents": outputs.get("documents", [])},
    )


def correctness_evaluator(inputs: dict, outputs: dict, reference_outputs: dict) -> dict:
    return _failed("correctness", outputs) or correctness_judge(
        inputs=inputs,
        outputs={"answer": outputs["answer"]},
        reference_outputs=reference_outputs,
    )