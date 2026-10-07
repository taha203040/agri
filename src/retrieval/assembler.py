# src/retrieval/assembler.py
from langchain_classic.retrievers import EnsembleRetriever
from langchain_core.tools import create_retriever_tool

from src.retrieval.retriever import (
    soil_retriever,
    disease_retriever,
    water_retriever,
    yield_retriever,
)
from src.retrieval.bm_search import (
    soil_bm25,
    disease_bm25,
    water_bm25,
    yield_bm25,
)


soil_hybrid = EnsembleRetriever(
    retrievers=[soil_bm25, soil_retriever],
    weights=[0.5, 0.5],
)

disease_hybrid = EnsembleRetriever(
    retrievers=[disease_bm25, disease_retriever],
    weights=[0.5, 0.5],
)

water_hybrid = EnsembleRetriever(
    retrievers=[water_bm25, water_retriever],
    weights=[0.5, 0.5],
)

yield_hybrid = EnsembleRetriever(
    retrievers=[yield_bm25, yield_retriever],
    weights=[0.5, 0.5],
)
# print(yield_hybrid)

soil_hybrid_tool = create_retriever_tool(
    retriever=soil_hybrid,
    name="soil_search",
    description=(
        "Search information about soil samples, "
        "soil types, nutrients, pH, and soil improvement."
    ),
)

disease_hybrid_tool = create_retriever_tool(
    retriever=disease_hybrid,
    name="disease_search",
    description=(
        "Search information about plant diseases, "
        "their causes, symptoms, and treatments."
    ),
)

water_hybrid_tool = create_retriever_tool(
    retriever=water_hybrid,
    name="water_search",
    description=(
        "Search information about irrigation, water consumption, "
        "moisture, and crop water requirements."
    ),
)

yield_hybrid_tool = create_retriever_tool(
    retriever=yield_hybrid,
    name="yield_search",
    description=(
        "Search information about crop yield forecasts, "
        "harvest timing, and production estimates."
    ),
)


HYBRID_TOOLS = [
    soil_hybrid_tool,
    disease_hybrid_tool,
    water_hybrid_tool,
    yield_hybrid_tool,
]