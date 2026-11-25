# =====================================================================
# OLD CODE (Chroma-based vectorstores) — commented out in favor of
# Pinecone. Kept for reference / rollback.
# =====================================================================
#
# from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
# from langchain_chroma import Chroma
# from langchain_core.embeddings import Embeddings
# # from langchain_huggingface import HuggingFaceEmbeddings
#
#
# # embeddings = HuggingFaceEmbeddings(
# #     model_name="BAAI/bge-small-en-v1.5",
# # )
#
#
# class ChromaDefaultEmbeddings(Embeddings):
#     """
#     LangChain `Embeddings` adapter around Chroma's built-in default embedder
#     (all-MiniLM-L6-v2 via ONNX).
#
#     Why this exists: `langchain-chroma` >= 1.x always opens collections with
#     `embedding_function=None`, and `chromadb` >= 1.x then refuses to embed
#     text ("You must provide an embedding function"). Passing this adapter keeps
#     the *same* embedding model these stores used before, so existing
#     collections stay valid and nothing needs to be re-ingested.
#     """
#
#     def __init__(self) -> None:
#         self._ef = DefaultEmbeddingFunction()
#
#     def _embed(self, texts: list[str]) -> list[list[float]]:
#         return [[float(x) for x in vec] for vec in self._ef(list(texts))]
#
#     def embed_documents(self, texts: list[str]) -> list[list[float]]:
#         return self._embed(texts)
#
#     def embed_query(self, text: str) -> list[float]:
#         return self._embed([text])[0]
#
#
# embeddings = ChromaDefaultEmbeddings()
#
#
# soil_vectorstore = Chroma(
#     collection_name="soil_collection",
#     persist_directory="./chroma_soil_db",
#     embedding_function=embeddings,
# )
#
#
# disease_vectorstore = Chroma(
#     collection_name="disease_collection",
#     persist_directory="./chroma_disease_db",
#     embedding_function=embeddings,
# )
#
#
# water_vectorstore = Chroma(
#     collection_name="water_collection",
#     persist_directory="./chroma_water_db",
#     embedding_function=embeddings,
# )
#
#
# yield_vectorstore = Chroma(
#     collection_name="yield_collection",
#     persist_directory="./chroma_yield_db",
#     embedding_function=embeddings,
# )
#
# =====================================================================

from functools import lru_cache

from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeEmbeddings, PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from src.config.settings import settings

# Hosted embedding model (multilingual: Arabic + English)
EMBEDDING_MODEL = "multilingual-e5-large"
EMBEDDING_DIM = 1024  # must match the model

_base_embeddings = PineconeEmbeddings(
    model=EMBEDDING_MODEL,
    pinecone_api_key=settings.pinecone_api_key,
)


@lru_cache(maxsize=512)
def _embed_query(text: str) -> tuple[float, ...]:
    return tuple(_base_embeddings.embed_query(text))


class CachedEmbeddings(Embeddings):
    """Caches query embeddings only. Documents are embedded once at ingest."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return _base_embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> list[float]:
        return list(_embed_query(text))


embeddings = CachedEmbeddings()

_pc = Pinecone(api_key=settings.pinecone_api_key)

if not _pc.has_index(settings.pinecone_index):
    _pc.create_index(
        name=settings.pinecone_index,
        dimension=EMBEDDING_DIM,
        metric="cosine",
        spec=ServerlessSpec(
            cloud=settings.pinecone_cloud,
            region=settings.pinecone_region,
        ),
    )

_index = _pc.Index(settings.pinecone_index)


def _store(namespace: str) -> PineconeVectorStore:
    return PineconeVectorStore(
        index=_index,
        embedding=embeddings,
        namespace=namespace,
    )


soil_vectorstore = _store("soil")
disease_vectorstore = _store("disease")  # crop_health shares this one
water_vectorstore = _store("water")
yield_vectorstore = _store("yield")
