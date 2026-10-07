from openevals.llm import create_llm_as_judge
from openevals.prompts import (
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