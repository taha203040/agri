from langchain_core.tools import create_retriever_tool

from src.config.settings import settings
from src.vectorstore.vector import (
    soil_vectorstore,
    disease_vectorstore,
    water_vectorstore,
    yield_vectorstore,
)

_K = {"k": settings.retrieval_k}

water_retriever = water_vectorstore.as_retriever(search_kwargs=_K)
crop_health_retriever = disease_vectorstore.as_retriever(search_kwargs=_K)
yield_retriever = yield_vectorstore.as_retriever(search_kwargs=_K)
soil_retriever = soil_vectorstore.as_retriever(search_kwargs=_K)
disease_retriever = disease_vectorstore.as_retriever(search_kwargs=_K)


soil_tool = create_retriever_tool(
    retriever=soil_retriever,
    name="soil_search",
    description=(
        "Search information about soil samples, "
        "soil types, nutrients, pH, and soil improvement."
    ),
)


disease_tool = create_retriever_tool(
    retriever=disease_retriever,
    name="disease_search",
    description=(
        "Search information about plant diseases, "
        "their causes, symptoms, and treatments."
    ),
)


TOOLS = [
    soil_tool,
    disease_tool,
]
