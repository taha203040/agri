# src/retrieval/bm_search.py
from langchain_community.retrievers import BM25Retriever

from src.config.settings import settings
from src.ingestion.loader import load_documents
from src.ingestion.splitter import split_documents


def _build(path: str):
    docs = load_documents(path)
    chunks = split_documents(docs)
    retriever = BM25Retriever.from_documents(chunks)
    retriever.k = settings.retrieval_k
    return docs, chunks, retriever


soil_docs, soil_chunks, soil_bm25 = _build("data/raw/soil")
disease_docs, disease_chunks, disease_bm25 = _build("data/raw/diseases")
water_docs, water_chunks, water_bm25 = _build("data/raw/water")
yield_docs, yield_chunks, yield_bm25 = _build("data/raw/yield")


if __name__ == "__main__":

    query = "How much water does a crop need?"

    results = water_bm25.invoke(query)

    print("\n=== BM25 TEST ===")
    print(f"Original documents : {len(water_docs)}")
    print(f"Chunks             : {len(water_chunks)}")
    print(f"Retrieved chunks   : {len(results)}")

    print("\n=== RESULTS ===")

    for i, doc in enumerate(results, 1):
        print(f"\n--- Result {i} ---")
        print(f"Characters: {len(doc.page_content)}")
        print(doc.page_content[:1000])
