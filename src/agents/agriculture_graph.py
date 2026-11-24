import operator
from functools import lru_cache
from pathlib import Path
from typing import Annotated, TypedDict

from langchain_core.messages import AnyMessage, SystemMessage
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from langgraph.types import Overwrite

from src.retrieval.assembler import (
    disease_hybrid,
    soil_hybrid,
    water_hybrid,
    yield_hybrid,
)

# ──────────────────────────────────────────────────────────────────────────────
# State
# ──────────────────────────────────────────────────────────────────────────────


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    intent: str
    # `operator.add` lets parallel nodes append without overwriting each other.
    # `classify_intent` resets it at the start of every turn (see below) so
    # retrieved context does not pile up in the checkpoint across turns.
    context: Annotated[list[str], operator.add]


# ──────────────────────────────────────────────────────────────────────────────
# Node 1: classify intent
# ──────────────────────────────────────────────────────────────────────────────
def classify_intent(state: AgentState) -> dict:
    q = state["messages"][-1].content.lower()

    intents = []

    # Soil / nutrient signals — check this FIRST, before crop_health,
    # because "leaf yellowing" would otherwise be captured by crop_health.
    soil_keywords = [
        "nutrient",
        "deficiency",
        "deficient",
        "nitrogen",
        "phosphorus",
        "potassium",
        "magnesium",
        "iron",
        "sulfur",
        "calcium",
        "zinc",
        "boron",
        "interveinal",
        "chlorosis",
        "yellowing",
        "yellow",
        "soil ph",
        "ph ",
        "calcareous",
        "saline",
        "sodic",
        "soil type",
        "sandy soil",
        "clay soil",
        "loam",
        "fertility",
        "fertilizer",
        "manure",
    ]
    if any(k in q for k in soil_keywords):
        intents.append("soil")

    # Water
    if any(
        k in q
        for k in [
            "water",
            "irrigation",
            "moisture",
            "rain",
            "evapotranspiration",
            "etc",
            "eto",
            "kc",
            "mm/day",
            "mm/season",
            "m³/ha",
            "crop coefficient",
            "drip",
            "sprinkler",
            "deficit irrigation",
        ]
    ):
        intents.append("water")

    # Crop health / disease (narrower than before — no more "leaf")
    if any(
        k in q
        for k in [
            "disease",
            "pest",
            "pathogen",
            "fungus",
            "fungal",
            "blight",
            "mildew",
            "rot",
            "wilt",
            "mosaic",
            "virus",
            "anthracnose",
            "rust",
            "spot",
            "scab",
            "canker",
        ]
    ):
        intents.append("crop_health")

    # Yield
    if any(
        k in q
        for k in [
            "yield",
            "harvest",
            "production",
            "forecast",
            "productivity",
            "harvest index",
            "yield gap",
        ]
    ):
        intents.append("yield")

    # Fallback: run everything (including soil)
    if not intents:
        intents = ["soil", "water", "crop_health", "yield"]

    # Fresh context per turn: with a checkpointer the `operator.add` reducer
    # would otherwise keep appending every turn's chunks to the same thread,
    # growing the stored state and feeding stale chunks into later answers.
    return {"intent": ",".join(intents), "context": Overwrite([])}


def soil_node(state):
    docs = soil_hybrid.invoke(state["messages"][-1].content)
    return {"context": [f"[soil] {d.page_content}" for d in docs]}


def crop_health_node(state):
    docs = disease_hybrid.invoke(state["messages"][-1].content)
    return {"context": [f"[crop_health] {d.page_content}" for d in docs]}


def water_node(state):
    docs = water_hybrid.invoke(state["messages"][-1].content)
    return {"context": [f"[water] {d.page_content}" for d in docs]}


def yield_node(state):
    docs = yield_hybrid.invoke(state["messages"][-1].content)
    return {"context": [f"[yield] {d.page_content}" for d in docs]}


# ──────────────────────────────────────────────────────────────────────────────
# Node 5: synthesize answer with LLM
# ──────────────────────────────────────────────────────────────────────────────
PROMPT_PATH = Path(__file__).parent / "prompts" / "synthesis.md"


@lru_cache(maxsize=1)
def get_synthesis_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


def synthesize(state: AgentState, config) -> dict:
    model: Runnable = config["configurable"]["model"]

    context_block = "\n\n".join(state.get("context", [])) or "(none)"

    system = SystemMessage(content=get_synthesis_prompt().format(context=context_block))

    response = model.invoke([system] + state["messages"])
    return {"messages": [response]}


def route_retrievers(state: AgentState) -> list[str]:
    routes = []
    intents = state["intent"].split(",")

    if "soil" in intents:
        routes.append("soil_node")
    if "water" in intents:
        routes.append("water_node")
    if "crop_health" in intents:
        routes.append("crop_health_node")
    if "yield" in intents:
        routes.append("yield_node")

    return routes or [
        "soil_node",
        "water_node",
        "crop_health_node",
        "yield_node",
    ]


# ──────────────────────────────────────────────────────────────────────────────
# Build the graph
# ──────────────────────────────────────────────────────────────────────────────
def build_agriculture_graph(model, checkpointer=None):
    builder = StateGraph(AgentState)

    # nodes — soil_node is now registered
    builder.add_node("classify", classify_intent)
    builder.add_node("soil_node", soil_node)
    builder.add_node("water_node", water_node)
    builder.add_node("crop_health_node", crop_health_node)
    builder.add_node("yield_node", yield_node)
    builder.add_node("synthesize", synthesize)

    # edges
    builder.add_edge(START, "classify")

    # fan-out: after classify, run one or more retrievers in parallel
    builder.add_conditional_edges(
        "classify",
        route_retrievers,
        [
            "soil_node",
            "water_node",
            "crop_health_node",
            "yield_node",
        ],
    )

    # fan-in: all retrievers go to synthesize
    builder.add_edge("soil_node", "synthesize")
    builder.add_edge("water_node", "synthesize")
    builder.add_edge("crop_health_node", "synthesize")
    builder.add_edge("yield_node", "synthesize")

    builder.add_edge("synthesize", END)

    graph = builder.compile(checkpointer=checkpointer)
    return graph.with_config({"configurable": {"model": model}})
