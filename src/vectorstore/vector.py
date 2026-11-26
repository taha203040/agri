import time
from functools import lru_cache
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from src.config.settings import settings

EMBEDDING_MODEL = "multilingual-e5-large"
EMBEDDING_DIM = 1024

# Initialize Pinecone client directly
_pc = Pinecone(api_key=settings.pinecone_api_key)

@lru_cache(maxsize=512)
def _embed_query(text: str) -> tuple[float, ...]:
    # Print to show that we are making the network call (cache miss)
    print(f"\n⏳ [EMBEDDING] Cache MISS. Sending query to Pinecone API: '{text[:30]}...'")
    start_time = time.time()

    try:
        response = _pc.inference.embed(
            model=EMBEDDING_MODEL,
            inputs=[text],
            parameters={"input_type": "query", "truncate": "END"}
        )

        end_time = time.time()
        print(f"✅ [EMBEDDING] Success! Took {end_time - start_time:.2f} seconds.")
        return tuple(response.data[0].values)

    except Exception as e:
        print(f"❌ [EMBEDDING] FAILED! Error: {e}")
        raise e

class CustomCachedEmbeddings(Embeddings):
    """Uses Pinecone's raw SDK for exact control over input_type."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        print(f"\n⏳ [EMBEDDING] Embedding {len(texts)} documents for ingestion...")
        start_time = time.time()

        response = _pc.inference.embed(
            model=EMBEDDING_MODEL,
            inputs=texts,
            parameters={"input_type": "passage", "truncate": "END"}
        )

        end_time = time.time()
        print(f"✅ [EMBEDDING] Documents embedded! Took {end_time - start_time:.2f} seconds.")
        return [item.values for item in response.data]

    def embed_query(self, text: str) -> list[float]:
        # If it's a cache hit, we print a message
        if _embed_query.cache_info().hits > 0:
            print(f"⚡ [EMBEDDING] Cache HIT. Retrieved vector for '{text[:30]}...' from memory instantly.")

        return list(_embed_query(text))

embeddings = CustomCachedEmbeddings()

# --- Database Setup ---
if not _pc.has_index(settings.pinecone_index):
    print("Creating new Pinecone index...")
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
disease_vectorstore = _store("disease")
water_vectorstore = _store("water")
yield_vectorstore = _store("yield")
