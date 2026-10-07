# src/retrieval/bm_search.py
from langchain_community.retrievers import BM25Retriever

from src.ingestion.loader import load_documents
from src.ingestion.splitter import split_documents


soil_docs = load_documents("data/raw/soil")
soil_chunks = split_documents(soil_docs)
soil_bm25 = BM25Retriever.from_documents(soil_chunks)
soil_bm25.k = 5


disease_docs = load_documents("data/raw/diseases")
disease_chunks = split_documents(disease_docs)
disease_bm25 = BM25Retriever.from_documents(disease_chunks)
disease_bm25.k = 5


water_docs = load_documents("data/raw/water")
water_chunks = split_documents(water_docs)
water_bm25 = BM25Retriever.from_documents(water_chunks)
water_bm25.k = 5


yield_docs = load_documents("data/raw/yield")
yield_chunks = split_documents(yield_docs)
yield_bm25 = BM25Retriever.from_documents(yield_chunks)
yield_bm25.k = 5
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